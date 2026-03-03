#!/usr/bin/env python3
"""
Collect data for repository improvement cycle.

This script fetches PRs, issues, and security data from GitHub
and stores them in .conductor/improvement-data/ for analysis.

Usage:
    python scripts/collect_improvement_data.py [--repo REPO] [--output DIR]

Examples:
    python scripts/collect_improvement_data.py
    python scripts/collect_improvement_data.py --repo edithatogo/conductor-next
    python scripts/collect_improvement_data.py --output ./improvement-data
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_gh_command(cmd: str, repo: str = None) -> list:
    """
    Run GitHub CLI command and parse JSON output.

    Args:
        cmd: GitHub CLI command (without 'gh' prefix)
        repo: Optional repository override

    Returns:
        Parsed JSON output as list/dict, or empty list on error
    """
    try:
        # Build full command
        full_cmd = f"gh {cmd} --json number,title,author,createdAt,updatedAt,labels,state"
        if repo:
            full_cmd = f"gh {cmd} --repo {repo} --json number,title,author,createdAt,updatedAt,labels,state"

        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=30)

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
    try:
        result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, timeout=10)
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
    try:
        # Try safety first
        result = subprocess.run(["safety", "check", "--json"], capture_output=True, text=True, timeout=60)
        if result.stdout:
            security_data["python_safety"] = json.loads(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Fallback to pip-audit
        try:
            result = subprocess.run(
                ["pip-audit", "-r", "requirements.txt", "-f", "json"], capture_output=True, text=True, timeout=60
            )
            if result.stdout:
                security_data["python_safety"] = json.loads(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            security_data["python_safety"] = {"error": "No Python security scanner available"}

    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(security_data, f, indent=2, ensure_ascii=False)

    # Calculate stats
    npm_vulns = sum(
        audit.get("metadata", {}).get("vulnerabilities", 0)
        for audit in security_data["npm_audits"].values()
        if isinstance(audit, dict) and "error" not in audit
    )

    return {
        "npm_vulnerabilities": npm_vulns,
        "python_vulnerabilities": len(security_data["python_safety"])
        if isinstance(security_data["python_safety"], list)
        else 0,
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

- `prs.json` - Pull request data
- `issues.json` - Issue data
- `security.json` - Security scan results
- `SUMMARY.md` - This summary

## Next Steps

1. Review open PRs (merge Dependabot, review community PRs)
2. Analyze high-priority issues
3. Address security vulnerabilities
4. Create improvement track based on findings
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
        "--output", type=Path, default=None, help="Output directory (default: .conductor/improvement-data/)"
    )

    parser.add_argument("--no-security", action="store_true", help="Skip security scanning")

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Set up output directory
    output_dir = args.output or (Path(".conductor") / "improvement-data")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("🚀 Starting improvement data collection...")
    print(f"Repository: {args.repo}")
    print(f"Output directory: {output_dir}")
    print()

    # Check GitHub CLI
    if not check_gh_installed():
        print("⚠️  Warning: GitHub CLI (gh) not installed or not authenticated.")
        print("   Install: https://cli.github.com/")
        print("   Authenticate: gh auth login")
        print()
        print("Continuing with limited data collection...")
        print()

    # Collect data
    stats = {}

    try:
        # Collect PRs
        prs_file = output_dir / "prs.json"
        stats["prs"] = collect_prs(args.repo, prs_file)
        print(f"  ✅ Collected {stats['prs']['open_total']} PRs")

        # Collect issues
        issues_file = output_dir / "issues.json"
        stats["issues"] = collect_issues(args.repo, issues_file)
        print(f"  ✅ Collected {stats['issues']['open_total']} issues")

        # Collect security data
        if not args.no_security:
            security_file = output_dir / "security.json"
            stats["security"] = collect_security_data(security_file)
            print("  ✅ Security scans complete")
        else:
            print("  ⏭️  Skipping security scans (--no-security)")
            stats["security"] = {}

        # Generate summary
        summary_file = output_dir / "SUMMARY.md"
        generate_summary(stats, summary_file)
        print("  ✅ Summary generated")

        print()
        print("📊 Collection Summary:")
        print(f"   PRs: {stats['prs']['open_total']} open ({stats['prs']['dependabot']} Dependabot)")
        print(f"   Issues: {stats['issues']['open_total']} open ({stats['issues']['high_priority']} high priority)")
        if not args.no_security:
            print(
                f"   Security: {stats['security'].get('npm_vulnerabilities', 0)} NPM, {stats['security'].get('python_vulnerabilities', 0)} Python vulnerabilities"
            )
        print()
        print(f"✅ Data collection complete! Review: {output_dir / 'SUMMARY.md'}")

    except Exception as e:
        print(f"\n❌ Error during collection: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
