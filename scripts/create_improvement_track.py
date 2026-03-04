#!/usr/bin/env python3
"""
Create improvement track from collected data.

This script analyzes collected improvement data and creates
a new Conductor track with prioritized tasks.

Usage:
    python scripts/create_improvement_track.py [--data DIR] [--output DIR]

Examples:
    python scripts/create_improvement_track.py
    python scripts/create_improvement_track.py --data .conductor/improvement-data
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List


def load_data(data_dir: Path) -> dict:
    """
    Load collected improvement data.

    Args:
        data_dir: Directory containing collected data files

    Returns:
        Dict with prs, issues, security data
    """
    data = {}

    # Load PRs
    prs_file = data_dir / "prs.json"
    if prs_file.exists():
        with open(prs_file, "r", encoding="utf-8") as f:
            data["prs"] = json.load(f)

    # Load issues
    issues_file = data_dir / "issues.json"
    if issues_file.exists():
        with open(issues_file, "r", encoding="utf-8") as f:
            data["issues"] = json.load(f)

    # Load security
    security_file = data_dir / "security.json"
    if security_file.exists():
        with open(security_file, "r", encoding="utf-8") as f:
            data["security"] = json.load(f)

    return data


def prioritize_prs(prs_data: dict) -> List[dict]:
    """
    Prioritize PRs for review.

    Args:
        prs_data: PR data from collection

    Returns:
        List of prioritized PR tasks
    """
    tasks = []
    open_prs = prs_data.get("open", [])

    # Group by type
    dependabot = [pr for pr in open_prs if "dependabot" in str(pr.get("author", {})).lower()]
    community = [pr for pr in open_prs if pr not in dependabot]

    # Add Dependabot tasks (high priority - security updates)
    for pr in dependabot:
        priority = "P0" if "security" in pr.get("title", "").lower() else "P1"
        tasks.append(
            {
                "title": f"Review and merge Dependabot PR #{pr['number']}",
                "priority": priority,
                "description": f"Merge dependency update: {pr['title']}",
                "pr_number": pr["number"],
            }
        )

    # Add community PR tasks
    for pr in community:
        tasks.append(
            {
                "title": f"Review community PR #{pr['number']}",
                "priority": "P1",
                "description": f"Review: {pr['title']}",
                "pr_number": pr["number"],
            }
        )

    return tasks


def prioritize_issues(issues_data: dict) -> List[dict]:
    """
    Prioritize issues for adoption.

    Args:
        issues_data: Issue data from collection

    Returns:
        List of prioritized issue tasks
    """
    tasks = []
    open_issues = issues_data.get("open", [])

    # Sort by priority
    for issue in open_issues:
        labels = [label.get("name", "").lower() for label in issue.get("labels", [])]

        # Determine priority
        if "p0" in labels:
            priority = "P0"
        elif "p1" in labels:
            priority = "P1"
        elif "bug" in labels:
            priority = "P1"
        elif "feature" in labels or "enhancement" in labels:
            priority = "P2"
        else:
            priority = "P3"

        tasks.append(
            {
                "title": f"Analyze upstream issue #{issue['number']}: {issue['title'][:50]}",
                "priority": priority,
                "description": issue["title"],
                "issue_number": issue["number"],
                "labels": labels,
            }
        )

    # Sort by priority
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    tasks.sort(key=lambda x: priority_order.get(x["priority"], 4))

    return tasks


def prioritize_security(security_data: dict) -> List[dict]:
    """
    Create security remediation tasks.

    Args:
        security_data: Security scan data

    Returns:
        List of security tasks
    """
    tasks = []

    # NPM vulnerabilities
    npm_audits = security_data.get("npm_audits", {})
    for dir, audit in npm_audits.items():
        if isinstance(audit, dict) and audit.get("vulnerabilities", 0) > 0:
            tasks.append(
                {
                    "title": f"Fix NPM vulnerabilities in {dir}",
                    "priority": "P0",
                    "description": f"Address {audit['vulnerabilities']} vulnerabilities",
                    "vulnerabilities": audit["vulnerabilities"],
                }
            )

    # Python vulnerabilities
    python_vulns = security_data.get("python_safety", [])
    if isinstance(python_vulns, list) and len(python_vulns) > 0:
        tasks.append(
            {
                "title": "Fix Python dependency vulnerabilities",
                "priority": "P0",
                "description": f"Address {len(python_vulns)} Python vulnerabilities",
                "vulnerabilities": len(python_vulns),
            }
        )

    return tasks


def generate_track_spec(tasks: dict, output_dir: Path):
    """
    Generate track specification and plan.

    Args:
        tasks: Dict with categorized tasks
        output_dir: Output directory for track
    """
    track_id = f"improvement_{datetime.now().strftime('%Y%m%d')}"
    track_dir = output_dir / track_id
    track_dir.mkdir(parents=True, exist_ok=True)

    # Generate spec.md
    spec_content = f"""# Repository Improvement Track - {datetime.now().strftime("%B %Y")}

**Track ID:** `{track_id}`  
**Created:** {datetime.now().strftime("%Y-%m-%d")}  
**Status:** Ready for Implementation  
**Priority:** P1-High  
**Duration:** 1-2 weeks

---

## Executive Summary

This track implements improvements based on automated data collection performed on {datetime.now().strftime("%Y-%m-%d")}.

**Key Findings:**
- PRs: {len(tasks.get("prs", []))} open PRs requiring review
- Issues: {len(tasks.get("issues", []))} upstream issues to analyze
- Security: {len(tasks.get("security", []))} security remediation tasks

---

## Data Sources

- `../.conductor/improvement-data/prs.json` - Pull request data
- `../.conductor/improvement-data/issues.json` - Issue data
- `../.conductor/improvement-data/security.json` - Security scan results

---

## Implementation Strategy

1. **Phase 1: Security First** - Address all P0 security vulnerabilities
2. **Phase 2: PR Management** - Review and merge open PRs
3. **Phase 3: Issue Analysis** - Analyze and prioritize upstream issues
4. **Phase 4: Implementation** - Implement selected improvements

---

## Success Criteria

- [ ] All P0 security vulnerabilities resolved
- [ ] All Dependabot PRs merged
- [ ] Community PRs reviewed
- [ ] Upstream issues analyzed and adoption decisions made
- [ ] Improvement track created for adopted issues

---

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    with open(track_dir / "spec.md", "w", encoding="utf-8") as f:
        f.write(spec_content)

    # Generate plan.md
    plan_content = f"""# Repository Improvement Track - Implementation Plan

**Track ID:** `{track_id}`  
**Created:** {datetime.now().strftime("%Y-%m-%d")}  
**Total Tasks:** {sum(len(v) for v in tasks.values())}

---

## Phase 1: Security Remediation [checkpoint: pending]

"""

    # Add security tasks
    for i, task in enumerate(tasks.get("security", []), 1):
        plan_content += f"""### Task 1.{i}: {task["title"]}
**Status:** [ ]  
**Priority:** {task["priority"]}  
**Description:** {task["description"]}

**Sub-tasks:**
- [ ] [TEST] Write test verifying vulnerability is fixed
- [ ] Review vulnerability details
- [ ] Update dependency to secure version
- [ ] Run tests to verify no regressions
- [ ] Commit with git note

---

"""

    plan_content += """## Phase 2: PR Review & Merge [checkpoint: pending]

"""

    # Add PR tasks
    for i, task in enumerate(tasks.get("prs", []), 1):
        plan_content += f"""### Task 2.{i}: {task["title"]}
**Status:** [ ]  
**Priority:** {task["priority"]}  
**PR:** #{task.get("pr_number", "N/A")}
**Description:** {task["description"]}

**Sub-tasks:**
- [ ] Review PR changes
- [ ] Check CI status
- [ ] Test locally if needed
- [ ] Merge or request changes
- [ ] Update plan with commit SHA

---

"""

    plan_content += """## Phase 3: Upstream Issue Analysis [checkpoint: pending]

"""

    # Add issue tasks
    for i, task in enumerate(tasks.get("issues", []), 1):
        plan_content += f"""### Task 3.{i}: {task["title"]}
**Status:** [ ]  
**Priority:** {task["priority"]}  
**Issue:** #{task.get("issue_number", "N/A")}
**Description:** {task["description"]}

**Sub-tasks:**
- [ ] Read issue details
- [ ] Assess relevance to our fork
- [ ] Decide: Adopt, Monitor, or Ignore
- [ ] If Adopt: Create implementation plan
- [ ] Document decision

---

"""

    plan_content += f"""## Checkpoints

### Phase 1 Checkpoint
**Status:** [ ]  
**Expected Date:** {datetime.now().strftime("%Y-%m-%d")} + 3 days

**Verification:**
- [ ] All P0 security vulnerabilities resolved
- [ ] Security scan clean

### Phase 2 Checkpoint
**Status:** [ ]  
**Expected Date:** {datetime.now().strftime("%Y-%m-%d")} + 1 week

**Verification:**
- [ ] All PRs reviewed
- [ ] Dependabot PRs merged
- [ ] Community PRs have decisions

### Phase 3 Checkpoint
**Status:** [ ]  
**Expected Date:** {datetime.now().strftime("%Y-%m-%d")} + 2 weeks

**Verification:**
- [ ] All issues analyzed
- [ ] Adoption decisions documented
- [ ] Improvement tracks created

---

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    with open(track_dir / "plan.md", "w", encoding="utf-8") as f:
        f.write(plan_content)

    return track_dir


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create improvement track from collected data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--data",
        type=Path,
        default=Path(".conductor") / "improvement-data",
        help="Directory containing collected data (default: .conductor/improvement-data)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("conductor") / "tracks",
        help="Output directory for track (default: conductor/tracks/)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    print("[TASK] Creating improvement track...")
    print(f"Data directory: {args.data}")
    print(f"Output directory: {args.output}")
    print()

    # Check data directory
    if not args.data.exists():
        print(f"[ERROR] Error: Data directory not found: {args.data}")
        print("   Run 'python scripts/collect_improvement_data.py' first")
        sys.exit(1)

    # Load data
    print("Loading collected data...")
    data = load_data(args.data)

    if not data:
        print(f"[ERROR] Error: No data found in {args.data}")
        sys.exit(1)

    print(f"  [OK] Loaded PRs: {len(data.get('prs', {}).get('open', []))} open")
    print(f"  [OK] Loaded Issues: {len(data.get('issues', {}).get('open', []))} open")
    print(f"  [OK] Loaded Security: {'Yes' if 'security' in data else 'No'}")
    print()

    # Prioritize tasks
    print("Prioritizing tasks...")
    tasks = {
        "security": prioritize_security(data.get("security", {})),
        "prs": prioritize_prs(data.get("prs", {})),
        "issues": prioritize_issues(data.get("issues", {})),
    }

    print(f"  Security tasks: {len(tasks['security'])}")
    print(f"  PR tasks: {len(tasks['prs'])}")
    print(f"  Issue tasks: {len(tasks['issues'])}")
    print()

    # Generate track
    print("Generating track specification and plan...")
    track_dir = generate_track_spec(tasks, args.output)

    print(f"  [OK] Track created: {track_dir}")
    print("     - spec.md")
    print("     - plan.md")
    print()

    # Summary
    total_tasks = sum(len(v) for v in tasks.values())
    print("[SUMMARY] Track Summary:")
    print(f"   Track ID: improvement_{datetime.now().strftime('%Y%m%d')}")
    print(f"   Total tasks: {total_tasks}")
    print("   Priority: P1-High")
    print("   Estimated duration: 1-2 weeks")
    print()
    print("[OK] Track creation complete!")
    print("   Start implementation: /conductor:implement")
    print(f"   Or review: /conductor:review {track_dir.name}")


if __name__ == "__main__":
    main()
