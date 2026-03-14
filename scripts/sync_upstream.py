#!/usr/bin/env python3
"""Upstream Sync Bot - Sync changes from upstream conductor repositories.

This script fetches changes from upstream repositories:
- gemini-cli-extensions/conductor
- jnorthrup/conductor2

It detects merge conflicts and creates draft PRs when needed.
"""

import os
import sys
import json
import hashlib
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from github import Github, Auth


class UpstreamSyncError(Exception):
    """Base exception for upstream sync errors."""
    pass


class GitHubClient:
    """GitHub API client for repository operations."""

    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token. Falls back to GITHUB_TOKEN env var.
        """
        self.token = token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise UpstreamSyncError(
                "GitHub token required. Set GH_TOKEN or GITHUB_TOKEN environment variable."
            )
        self.auth = Auth.Token(self.token)
        self.gh = Github(auth=self.auth)
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def get_repo(self, repo_name: str) -> dict:
        """Fetch repository information.

        Args:
            repo_name: Repository name in format 'owner/repo'

        Returns:
            Repository data as dict
        """
        url = f"{self.api_base}/repos/{repo_name}"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_branch(self, repo_name: str, branch: str = "main") -> dict:
        """Fetch branch information.

        Args:
            repo_name: Repository name in format 'owner/repo'
            branch: Branch name

        Returns:
            Branch data as dict
        """
        url = f"{self.api_base}/repos/{repo_name}/branches/{branch}"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def compare_branches(
        self, base_repo: str, head_repo: str, base_branch: str = "main", head_branch: str = "main"
    ) -> dict:
        """Compare two branches across repositories.

        Args:
            base_repo: Base repository (owner/repo)
            head_repo: Head repository (owner/repo)
            base_branch: Base branch name
            head_branch: Head branch name

        Returns:
            Comparison data including commits ahead/behind
        """
        url = f"{self.api_base}/repos/{base_repo}/compare/{base_branch}...{head_repo}:{head_branch}"
        response = requests.get(url, headers=self.headers, timeout=30)
        if response.status_code == 404:
            return {"status": "diverged", "ahead_by": 0, "behind_by": 0, "commits": []}
        response.raise_for_status()
        return response.json()

    def create_pull_request(
        self,
        repo_name: str,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        draft: bool = True,
    ) -> dict:
        """Create a pull request.

        Args:
            repo_name: Repository name (owner/repo)
            title: PR title
            body: PR description
            head: Head branch name
            base: Base branch name
            draft: Whether to create as draft

        Returns:
            PR data as dict
        """
        url = f"{self.api_base}/repos/{repo_name}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
            "draft": draft,
        }
        response = requests.post(url, headers=self.headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()


class SyncState:
    """Track sync state and history."""

    def __init__(self, state_file: Path):
        """Initialize sync state tracker.

        Args:
            state_file: Path to state JSON file
        """
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """Load state from file or create new."""
        if self.state_file.exists():
            with open(self.state_file, "r") as f:
                return json.load(f)
        return {
            "last_sync": None,
            "upstreams": {},
            "sync_log": [],
        }

    def save(self):
        """Save state to file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def update_sync(self, upstream: str, commit_sha: str, status: str):
        """Update sync state for an upstream.

        Args:
            upstream: Upstream repository name
            commit_sha: Latest synced commit SHA
            status: Sync status (success, failed, skipped)
        """
        self.state["upstreams"][upstream] = {
            "last_sync": datetime.now(timezone.utc).isoformat(),
            "commit_sha": commit_sha,
            "status": status,
        }
        self.state["sync_log"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "upstream": upstream,
            "commit_sha": commit_sha,
            "status": status,
        })
        # Keep only last 100 log entries
        self.state["sync_log"] = self.state["sync_log"][-100:]
        self.save()


class UpstreamSyncBot:
    """Main sync bot orchestrator."""

    def __init__(
        self,
        target_repo: str,
        upstreams: list[str],
        state_file: Path,
        *,
        dry_run: bool = False,
        create_prs: bool = False,
    ):
        """Initialize sync bot.

        Args:
            target_repo: Target repository to sync to (owner/repo)
            upstreams: List of upstream repositories to sync from
            state_file: Path to state tracking file
        """
        self.target_repo = target_repo
        self.upstreams = upstreams
        self.dry_run = dry_run
        self.create_prs = create_prs
        self.client = GitHubClient()
        self.state = SyncState(state_file)
        self.repo_root = Path(self._run_git(["rev-parse", "--show-toplevel"]).stdout.strip())

    def _run_git(
        self,
        args: list[str],
        *,
        cwd: Optional[Path] = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        """Run a git command and optionally fail with detailed context."""
        result = subprocess.run(
            ["git", *args],
            cwd=cwd or Path.cwd(),
            check=False,
            capture_output=True,
            text=True,
        )
        if check and result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
            raise UpstreamSyncError(f"git {' '.join(args)} failed: {detail}")
        return result

    def _resolve_upstream_branch(self, upstream: str, preferred_branch: str) -> str:
        """Resolve the branch to sync from for an upstream repository."""
        repo_data = self.client.get_repo(upstream)
        default_branch = repo_data.get("default_branch", "main")

        for candidate in [preferred_branch, default_branch]:
            try:
                self.client.get_branch(upstream, candidate)
                return candidate
            except requests.HTTPError as exc:
                if exc.response is None or exc.response.status_code != 404:
                    raise

        raise UpstreamSyncError(
            f"Could not resolve an upstream branch for {upstream} "
            f"(preferred={preferred_branch}, default={default_branch})"
        )

    def _build_pr_body(
        self,
        upstream: str,
        upstream_sha: str,
        *,
        upstream_branch: str,
        sync_mode: str,
        details: str = "",
    ) -> str:
        extra = f"\n### Notes\n{details}\n" if details else ""
        return f"""## Upstream Sync

Automated sync from [{upstream}](https://github.com/{upstream})

**Upstream Branch:** `{upstream_branch}`
**Upstream Commit:** `{upstream_sha[:7]}`
**Sync Time:** {datetime.now(timezone.utc).isoformat()}
**Mode:** `{sync_mode}`

### Changes
- Automated upstream sync via sync_upstream.py
- Review changes before merging
{extra}
---
*This PR was created automatically by the Upstream Sync Bot*
"""

    def _create_conflict_report(
        self,
        worktree_dir: Path,
        *,
        upstream: str,
        upstream_branch: str,
        upstream_sha: str,
        branch_name: str,
        merge_result: subprocess.CompletedProcess[str],
    ) -> Path:
        report_dir = worktree_dir / ".github" / "upstream-sync"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"{branch_name.replace('/', '_')}.md"
        report_path.write_text(
            "\n".join(
                [
                    f"# Manual Sync Review: {upstream}",
                    "",
                    f"- Upstream branch: `{upstream_branch}`",
                    f"- Upstream commit: `{upstream_sha}`",
                    f"- Generated: {datetime.now(timezone.utc).isoformat()}",
                    "",
                    "## Merge Output",
                    "```text",
                    (merge_result.stdout or "").strip(),
                    (merge_result.stderr or "").strip(),
                    "```",
                    "",
                    "## Follow-up",
                    "- Resolve the merge manually on this branch.",
                    "- Re-run tests before merging.",
                ]
            ).strip()
            + "\n",
            encoding="utf-8",
        )
        return report_path

    def fetch_upstream(self, upstream: str, preferred_branch: str) -> dict:
        """Fetch upstream repository information.

        Args:
            upstream: Upstream repository name

        Returns:
            Upstream repo and branch data
        """
        upstream_branch = self._resolve_upstream_branch(upstream, preferred_branch)
        print(f"[FETCH] Fetching {upstream}@{upstream_branch}...")
        repo_data = self.client.get_repo(upstream)
        branch_data = self.client.get_branch(upstream, upstream_branch)
        return {
            "repo": repo_data,
            "branch": branch_data,
            "branch_name": upstream_branch,
            "sha": branch_data["commit"]["sha"],
        }

    def compare_upstream(
        self,
        upstream: str,
        *,
        target_branch: str = "main",
        upstream_branch: str = "main",
    ) -> dict:
        """Compare target and upstream branches.

        Args:
            upstream: Upstream repository name
            target_branch: Target branch name
            upstream_branch: Upstream branch name

        Returns:
            GitHub comparison payload
        """
        try:
            return self.client.compare_branches(
                self.target_repo, upstream, target_branch, upstream_branch
            )
        except Exception as e:
            print(f"[WARN] Could not compare branches: {e}")
            return {"status": "unknown", "ahead_by": 0, "behind_by": 0, "commits": []}

    def create_sync_pr(
        self,
        upstream: str,
        upstream_sha: str,
        *,
        upstream_branch: str,
        target_branch: str = "main",
        comparison_status: str = "ahead",
    ) -> Optional[dict]:
        """Create a PR for upstream changes.

        Args:
            upstream: Upstream repository name
            upstream_sha: Latest commit SHA from upstream
            target_branch: Target branch name

        Returns:
            PR data if created, None otherwise
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        upstream_name = upstream.replace("/", "-")
        branch_name = f"sync/{upstream_name}_{timestamp}"
        title = f"Sync from {upstream}"

        print(f"[PLAN] Preparing upstream sync PR: {title}")
        print(f"     Branch: {branch_name}")
        print(f"     From: {upstream}@{upstream_branch}")
        print(f"     To: {self.target_repo}:{target_branch}")

        if self.dry_run:
            return {
                "title": title,
                "body": self._build_pr_body(
                    upstream,
                    upstream_sha,
                    upstream_branch=upstream_branch,
                    sync_mode="dry_run",
                    details=f"Comparison status: {comparison_status}",
                ),
                "head": branch_name,
                "base": target_branch,
                "draft": True,
                "dry_run": True,
            }

        worktree_dir = Path(tempfile.mkdtemp(prefix="conductor-sync-"))
        worktree_added = False
        sync_mode = "merge"
        details = f"Comparison status: {comparison_status}"

        try:
            self._run_git(["worktree", "add", "--detach", str(worktree_dir), target_branch], cwd=self.repo_root)
            worktree_added = True
            self._run_git(["switch", "-c", branch_name], cwd=worktree_dir)
            self._run_git(
                ["config", "user.name", "github-actions[bot]"],
                cwd=worktree_dir,
            )
            self._run_git(
                ["config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"],
                cwd=worktree_dir,
            )

            self._run_git(
                ["fetch", "--no-tags", f"https://github.com/{upstream}.git", upstream_branch],
                cwd=worktree_dir,
            )
            merge_result = self._run_git(
                ["merge", "--no-ff", "--no-edit", "FETCH_HEAD"],
                cwd=worktree_dir,
                check=False,
            )

            if merge_result.returncode != 0:
                sync_mode = "conflict_report"
                self._run_git(["merge", "--abort"], cwd=worktree_dir, check=False)
                report_path = self._create_conflict_report(
                    worktree_dir,
                    upstream=upstream,
                    upstream_branch=upstream_branch,
                    upstream_sha=upstream_sha,
                    branch_name=branch_name,
                    merge_result=merge_result,
                )
                self._run_git(["add", str(report_path.relative_to(worktree_dir))], cwd=worktree_dir)
                self._run_git(
                    ["commit", "-m", f"chore(sync): record manual sync review for {upstream}"],
                    cwd=worktree_dir,
                )
                details = (
                    f"Comparison status: {comparison_status}\n"
                    f"Merge conflicts were detected. Review `{report_path.relative_to(worktree_dir)}`."
                )

            self._run_git(["push", "-u", "origin", branch_name], cwd=worktree_dir)
            pr = self.client.create_pull_request(
                self.target_repo,
                title,
                self._build_pr_body(
                    upstream,
                    upstream_sha,
                    upstream_branch=upstream_branch,
                    sync_mode=sync_mode,
                    details=details,
                ),
                branch_name,
                target_branch,
                draft=True,
            )
            pr["sync_mode"] = sync_mode
            return pr
        finally:
            if worktree_added:
                self._run_git(["worktree", "remove", "--force", str(worktree_dir)], cwd=self.repo_root, check=False)
            shutil.rmtree(worktree_dir, ignore_errors=True)

    def sync(self, target_branch: str = "main") -> dict:
        """Run the sync process for all upstreams.

        Args:
            target_branch: Target branch name in local repository

        Returns:
            Sync results summary
        """
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target": self.target_repo,
            "upstreams": [],
        }

        for upstream in self.upstreams:
            print(f"\n{'='*60}")
            print(f"[SYNC] Processing upstream: {upstream}")
            print(f"{'='*60}")

            try:
                # Fetch upstream
                upstream_data = self.fetch_upstream(upstream, target_branch)
                upstream_sha = upstream_data["sha"]
                upstream_branch = upstream_data["branch_name"]

                print(f"[INFO] Latest commit: {upstream_sha[:7]} ({upstream_branch})")

                comparison = self.compare_upstream(
                    upstream,
                    target_branch=target_branch,
                    upstream_branch=upstream_branch,
                )
                comparison_status = comparison.get("status", "unknown")
                ahead_by = comparison.get("ahead_by", 0)
                behind_by = comparison.get("behind_by", 0)
                print(
                    f"[INFO] Comparison status: {comparison_status} "
                    f"(ahead_by={ahead_by}, behind_by={behind_by})"
                )

                if comparison_status in {"identical", "behind"}:
                    print("[OK] No upstream changes require a sync PR.")
                    self.state.update_sync(upstream, upstream_sha, "up_to_date")
                    results["upstreams"].append({
                        "name": upstream,
                        "sha": upstream_sha,
                        "branch": upstream_branch,
                        "status": "up_to_date",
                        "comparison_status": comparison_status,
                    })
                elif self.create_prs:
                    pr = self.create_sync_pr(
                        upstream,
                        upstream_sha,
                        upstream_branch=upstream_branch,
                        target_branch=target_branch,
                        comparison_status=comparison_status,
                    )
                    sync_status = "review_required" if pr.get("sync_mode") == "conflict_report" else "pr_created"
                    self.state.update_sync(upstream, upstream_sha, sync_status)
                    results["upstreams"].append({
                        "name": upstream,
                        "sha": upstream_sha,
                        "branch": upstream_branch,
                        "status": sync_status,
                        "comparison_status": comparison_status,
                        "pr": pr,
                    })
                else:
                    print("[INFO] Upstream changes detected, but PR creation is disabled for this run.")
                    observed_status = "review_required" if comparison_status == "diverged" else "changes_detected"
                    self.state.update_sync(upstream, upstream_sha, observed_status)
                    results["upstreams"].append({
                        "name": upstream,
                        "sha": upstream_sha,
                        "branch": upstream_branch,
                        "status": observed_status,
                        "comparison_status": comparison_status,
                    })

            except Exception as e:
                print(f"[ERROR] Failed to sync {upstream}: {e}")
                self.state.update_sync(upstream, "", "failed")
                results["upstreams"].append({
                    "name": upstream,
                    "status": "failed",
                    "error": str(e),
                })

        # Save state
        self.state.save()

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Sync changes from upstream repositories")
    parser.add_argument(
        "--target",
        default="edithatogo/conductor-next",
        help="Target repository (default: edithatogo/conductor-next)",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Target branch in local repository (default: main)",
    )
    parser.add_argument(
        "--upstream",
        action="append",
        default=[
            "gemini-cli-extensions/conductor",
            "jnorthrup/conductor2",
        ],
        help="Upstream repositories to sync from",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=Path(".github/sync_state.json"),
        help="Path to sync state file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making changes",
    )
    parser.add_argument(
        "--create-pr",
        action="store_true",
        help="Create and push a draft pull request branch when upstream changes are detected",
    )

    args = parser.parse_args()

    print("="*60)
    print("Upstream Sync Bot")
    print("="*60)
    print(f"Target: {args.target}")
    print(f"Branch: {args.branch}")
    print(f"Upstreams: {', '.join(args.upstream)}")
    print(f"State file: {args.state_file}")
    print(f"Dry run: {args.dry_run}")
    print(f"Create PRs: {args.create_pr}")
    print("="*60)

    if args.dry_run:
        print("[DRY RUN] No changes will be made")
        return 0

    try:
        bot = UpstreamSyncBot(
            args.target,
            args.upstream,
            args.state_file,
            dry_run=args.dry_run,
            create_prs=args.create_pr,
        )
        results = bot.sync(target_branch=args.branch)

        print("\n" + "="*60)
        print("Sync Summary")
        print("="*60)
        for upstream_result in results["upstreams"]:
            status = upstream_result.get("status", "unknown")
            name = upstream_result.get("name", "unknown")
            sha = upstream_result.get("sha", "")[:7] if upstream_result.get("sha") else "N/A"
            print(f"  {name}: {status} ({sha})")

        # Return non-zero if any failures
        failures = sum(1 for r in results["upstreams"] if r.get("status") == "failed")
        return 1 if failures > 0 else 0

    except UpstreamSyncError as e:
        print(f"[FATAL] {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
