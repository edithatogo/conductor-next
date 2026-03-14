#!/usr/bin/env python3
"""
Collect data for repository improvement cycle.

This script fetches PRs, issues, security data, and upstream branch information
from GitHub and stores them in .conductor/improvement-data/ for analysis.

Usage:
    python scripts/collect_improvement_data.py [--repo REPO] [--upstream REPO] [--output DIR]

Examples:
    python scripts/collect_improvement_data.py
    python scripts/collect_improvement_data.py --repo edithatogo/conductor-next --upstream gemini-cli-extensions/conductor
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _gh_env() -> dict:
    """Return environment for gh commands, preserving workflow tokens."""
    env = os.environ.copy()
    if env.get("GITHUB_TOKEN") and not env.get("GH_TOKEN"):
        env["GH_TOKEN"] = env["GITHUB_TOKEN"]
    return env


def _extract_npm_vulnerability_total(audit: dict) -> int:
    """Normalize npm audit vulnerability counts across npm output formats."""
    vulnerabilities = audit.get("metadata", {}).get("vulnerabilities", 0)
    if isinstance(vulnerabilities, int):
        return vulnerabilities
    if isinstance(vulnerabilities, dict):
        return sum(value for value in vulnerabilities.values() if isinstance(value, int))
    return 0


def _python_dependency_manifest() -> Path | None:
    """Return the Python dependency manifest used for security checks."""
    requirements = Path("requirements.txt")
    return requirements if requirements.exists() else None


def _count_python_vulnerabilities(results: list | dict) -> int:
    """Count actual Python vulnerabilities, excluding scanner errors."""
    if isinstance(results, list):
        return sum(1 for item in results if isinstance(item, dict) and "error" not in item)
    return 0


def run_gh_command(cmd: str, repo: str = None, json_fields: str = None) -> list:
    """
    Run GitHub CLI command and parse JSON output.

    Args:
        cmd: GitHub CLI command (without 'gh' prefix)
        repo: Optional repository override
        json_fields: Optional JSON fields to return

    Returns:
        Parsed JSON output as list/dict, or empty list on error
    """
    try:
        # Default fields
        fields = json_fields or "number,title,author,createdAt,updatedAt,labels,state"
        
        # Build full command
        full_cmd = f"gh {cmd} --json {fields}"
        if repo:
            full_cmd = f"gh {cmd} --repo {repo} --json {fields}"

        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            env=_gh_env(),
        )

        if result.returncode != 0:
            print(f"Warning: Command failed: {full_cmd}", file=sys.stderr)
            if result.stderr:
                print(f"Error: {result.stderr}", file=sys.stderr)
            return []

        return json.loads(result.stdout) if result.stdout else []

    except subprocess.TimeoutExpired:
        print(f"Warning: Command timed out: {cmd}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse JSON output: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Warning: Unexpected error: {e}", file=sys.stderr)
        return []


def check_gh_installed() -> bool:
    """
    Check if GitHub CLI is installed and authenticated.

    Returns:
        True if gh is available and authenticated, False otherwise
    """
    env = _gh_env()
    if env.get("GH_TOKEN"):
        return True
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def collect_prs(repo: str, output_file: Path) -> dict:
    """
    Collect pull requests data.

    Args:
        repo: Repository name in format owner/repo
        output_file: Path to output JSON file

    Returns:
        Dict with PR statistics
    """
    print(f"Fetching PRs from {repo}...")

    # Fetch open PRs
    open_prs = run_gh_command("pr list --state open --limit 100", repo)

    # Fetch closed PRs (last 30 days)
    closed_prs = run_gh_command(
        f"pr list --state closed --search 'merged:>={(datetime.now().replace(day=1)).strftime('%Y-%m-%d')}' --limit 100",
        repo,
    )

    # Save to file
    data = {"open": open_prs, "closed": closed_prs, "fetched_at": datetime.now().isoformat()}

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Calculate stats
    dependabot_prs = sum(1 for pr in open_prs if "dependabot" in str(pr.get("author", {})).lower())
    community_prs = len(open_prs) - dependabot_prs

    return {
        "open_total": len(open_prs),
        "dependabot": dependabot_prs,
        "community": community_prs,
        "closed_recent": len(closed_prs),
    }


def collect_issues(repo: str, output_file: Path) -> dict:
    """
    Collect issues data.

    Args:
        repo: Repository name in format owner/repo
        output_file: Path to output JSON file

    Returns:
        Dict with issue statistics
    """
    print(f"Fetching issues from {repo}...")

    # Fetch open issues
    open_issues = run_gh_command("issue list --state open --limit 100", repo)

    # Save to file
    data = {"open": open_issues, "fetched_at": datetime.now().isoformat()}

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Calculate stats
    p0_p1_issues = sum(
        1
        for issue in open_issues
        if any(label.get("name", "").lower() in ["p0", "p1"] for label in issue.get("labels", []))
    )

    return {"open_total": len(open_issues), "high_priority": p0_p1_issues}


def collect_upstream_branches(upstream_repo: str, output_file: Path) -> dict:
    """
    Collect upstream branch data (dev, beta, staging).

    Args:
        upstream_repo: Upstream repository name
        output_file: Path to output JSON file

    Returns:
        Dict with branch statistics
    """
    print(f"Fetching branches from upstream {upstream_repo}...")
    
    # Using gh api to get branches as gh branch command is local-only
    try:
        cmd = f"gh api repos/{upstream_repo}/branches"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            env=_gh_env(),
        )
        
        if result.returncode != 0:
            print(f"Warning: Failed to fetch upstream branches: {upstream_repo}", file=sys.stderr)
            return {"branches": [], "error": result.stderr}
            
        branches = json.loads(result.stdout)
        
        # Filter for dev/beta/staging
        interesting_patterns = ["dev", "beta", "staging", "develop", "next"]
        interesting_branches = [
            b for b in branches 
            if any(pattern in b["name"].lower() for pattern in interesting_patterns)
        ]
        
        data = {
            "all_branches": [b["name"] for b in branches],
            "beta_branches": interesting_branches,
            "upstream_repo": upstream_repo,
            "fetched_at": datetime.now().isoformat()
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        return {
            "total_branches": len(branches),
            "beta_branches_count": len(interesting_branches),
            "beta_branch_names": [b["name"] for b in interesting_branches]
        }
        
    except Exception as e:
        print(f"Warning: Error collecting upstream branches: {e}", file=sys.stderr)
        return {"error": str(e)}


def collect_security_data(output_file: Path) -> dict:
    """
    Collect security scan data.

    Args:
        output_file: Path to output JSON file

    Returns:
        Dict with security scan results
    """
    print("Running security scans...")

    security_data = {"npm_audits": {}, "python_safety": [], "scanned_at": datetime.now().isoformat()}

    # NPM audits (for Node.js projects)
    npm_dirs = ["mcp-server", "conductor-vscode", "mcp"]
    for npm_dir in npm_dirs:
        npm_path = Path(npm_dir)
        if npm_path.exists() and (npm_path / "package.json").exists():
            print(f"  Running npm audit in {npm_dir}...")
            try:
                result = subprocess.run(
                    ["npm", "audit", "--json"], cwd=npm_dir, capture_output=True, text=True, timeout=60
                )
                if result.stdout:
                    try:
                        security_data["npm_audits"][npm_dir] = json.loads(result.stdout)
                    except json.JSONDecodeError:
                        security_data["npm_audits"][npm_dir] = {"error": "Invalid JSON output"}
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                security_data["npm_audits"][npm_dir] = {"error": str(e)}

    # Python safety check
    print("  Running Python dependency check...")
    requirements = _python_dependency_manifest()
    try:
        # Try safety first
        result = subprocess.run(["safety", "check", "--json"], capture_output=True, text=True, timeout=60)
        if result.stdout:
            try:
                security_data["python_safety"] = json.loads(result.stdout)
            except json.JSONDecodeError:
                security_data["python_safety"] = []
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Fallback to pip-audit
        pass

    if security_data["python_safety"] == []:
        if requirements is not None:
            try:
                result = subprocess.run(
                    ["pip-audit", "-r", str(requirements), "-f", "json"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.stdout:
                    security_data["python_safety"] = json.loads(result.stdout)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                security_data["python_safety"] = {"error": "No Python security scanner available"}
        else:
            security_data["python_safety"] = {"error": "No requirements.txt found for pip-audit"}

    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(security_data, f, indent=2, ensure_ascii=False)

    # Calculate stats
    npm_vulns = sum(
        _extract_npm_vulnerability_total(audit)
        for audit in security_data["npm_audits"].values()
        if isinstance(audit, dict) and "error" not in audit
    )

    return {
        "npm_vulnerabilities": npm_vulns,
        "python_vulnerabilities": _count_python_vulnerabilities(security_data["python_safety"]),
    }


def generate_summary(stats: dict, output_file: Path):
    """
    Generate summary report.

    Args:
        stats: Combined statistics from all collection steps
        output_file: Path to output markdown file
    """
    print("Generating summary report...")

    summary = f"""# Improvement Data Collection Summary

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Upstream Synchronization (Beta Tool)

| Metric | Value |
|--------|-------|
| Upstream Repo | {stats.get("upstream", {}).get("upstream_repo", "N/A")} |
| Total Branches | {stats.get("upstream", {}).get("total_branches", "N/A")} |
| Beta/Dev Branches | {stats.get("upstream", {}).get("beta_branches_count", "N/A")} |
| Target Branches | {", ".join(stats.get("upstream", {}).get("beta_branch_names", [])) or "None detected"} |

## Pull Requests

| Metric | Value |
|--------|-------|
| Open PRs | {stats.get("prs", {}).get("open_total", "N/A")} |
| Dependabot PRs | {stats.get("prs", {}).get("dependabot", "N/A")} |
| Community PRs | {stats.get("prs", {}).get("community", "N/A")} |
| Closed (Recent) | {stats.get("prs", {}).get("closed_recent", "N/A")} |

## Issues

| Metric | Value |
|--------|-------|
| Open Issues | {stats.get("issues", {}).get("open_total", "N/A")} |
| High Priority (P0/P1) | {stats.get("issues", {}).get("high_priority", "N/A")} |

## Security

| Metric | Value |
|--------|-------|
| NPM Vulnerabilities | {stats.get("security", {}).get("npm_vulnerabilities", "N/A")} |
| Python Vulnerabilities | {stats.get("security", {}).get("python_vulnerabilities", "N/A")} |

## Files Generated

- `upstream.json` - Upstream branch data (New)
- `prs.json` - Pull request data
- `issues.json` - Issue data
- `security.json` - Security scan results
- `SUMMARY.md` - This summary

## Next Steps

1. **Sync & Merge:** Analyze upstream dev/beta branches for merging
2. **Deprecation Audit:** Identify local features redundant with upstream
3. **PR Review:** Merge Dependabot and review community PRs
4. **Security:** Fix high-priority vulnerabilities
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Collect data for repository improvement cycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--repo", default="edithatogo/conductor-next", help="Repository to analyze (default: edithatogo/conductor-next)"
    )
    
    parser.add_argument(
        "--upstream", default="gemini-cli-extensions/conductor", help="Upstream repository (default: gemini-cli-extensions/conductor)"
    )

    parser.add_argument(
        "--output", type=Path, default=None, help="Output directory (default: .conductor/improvement-data/)"
    )

    parser.add_argument("--no-security", action="store_true", help="Skip security scanning")

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Set up output directory
    output_dir = args.output or (Path(".conductor") / "improvement-data")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[READY] Starting improvement data collection...")
    print(f"Repository: {args.repo}")
    print(f"Upstream:   {args.upstream}")
    print(f"Output directory: {output_dir}")
    print()

    # Check GitHub CLI
    if not check_gh_installed():
        print("[WARNING]  Warning: GitHub CLI (gh) not installed or not authenticated.")
        print("   Install: https://cli.github.com/")
        print("   Authenticate: gh auth login")
        print()
        print("Continuing with limited data collection...")
        print()

    # Collect data
    stats = {}

    try:
        # Collect Upstream branches
        upstream_file = output_dir / "upstream.json"
        stats["upstream"] = collect_upstream_branches(args.upstream, upstream_file)
        stats["upstream"]["upstream_repo"] = args.upstream
        print(f"  [OK] Collected {stats['upstream'].get('beta_branches_count', 0)} beta/dev branches")

        # Collect PRs
        prs_file = output_dir / "prs.json"
        stats["prs"] = collect_prs(args.repo, prs_file)
        print(f"  [OK] Collected {stats['prs']['open_total']} PRs")

        # Collect issues
        issues_file = output_dir / "issues.json"
        stats["issues"] = collect_issues(args.repo, issues_file)
        print(f"  [OK] Collected {stats['issues']['open_total']} issues")

        # Collect security data
        if not args.no_security:
            security_file = output_dir / "security.json"
            stats["security"] = collect_security_data(security_file)
            print("  [OK] Security scans complete")
        else:
            print("  [SKIP]  Skipping security scans (--no-security)")
            stats["security"] = {}

        # Generate summary
        summary_file = output_dir / "SUMMARY.md"
        generate_summary(stats, summary_file)
        print("  [OK] Summary generated")

        print()
        print("[SUMMARY] Collection Summary:")
        print(f"   Upstream: {stats['upstream'].get('beta_branches_count', 0)} dev branches found")
        print(f"   PRs: {stats['prs']['open_total']} open ({stats['prs']['dependabot']} Dependabot)")
        print(f"   Issues: {stats['issues']['open_total']} open ({stats['issues']['high_priority']} high priority)")
        if not args.no_security:
            print(
                f"   Security: {stats['security'].get('npm_vulnerabilities', 0)} NPM, {stats['security'].get('python_vulnerabilities', 0)} Python vulnerabilities"
            )
        print()
        print(f"[OK] Data collection complete! Review: {output_dir / 'SUMMARY.md'}")

    except Exception as e:
        print(f"\n[ERROR] Error during collection: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
