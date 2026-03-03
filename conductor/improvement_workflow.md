# Repository Improvement Workflow

**Version:** 1.0  
**Effective Date:** March 3, 2026  
**Review Cycle:** Monthly (or after major upstream changes)

---

## Purpose

This workflow defines the standard process for conducting regular repository improvements, ensuring:
- Continuous integration of upstream improvements
- Proactive security and dependency management
- Strategic alignment with fork goals
- Ralph Mode-enabled self-improvement

---

## Trigger Conditions

This workflow should be executed:
- [ ] **Monthly** (scheduled)
- [ ] **After major upstream releases** (event-driven)
- [ ] **When security vulnerabilities detected** (urgent)
- [ ] **When technical debt accumulates** (threshold-based)
- [ ] **On-demand** (ad-hoc improvements)

---

## Roles & Responsibilities

| Role | Responsibilities | Time Commitment |
|------|-----------------|-----------------|
| **Improvement Lead** | Overall coordination, prioritization | 4-6 hours/week |
| **Security Reviewer** | Security audit, vulnerability assessment | 2-3 hours |
| **PR Reviewer** | Review and merge community PRs | 2-3 hours |
| **Upstream Monitor** | Track upstream issues/PRs | 1-2 hours |
| **Ralph Mode** | Autonomous implementation (if enabled) | Automated |

---

## Workflow Phases

### Phase 1: Data Collection (Day 1)

**Duration:** 2-3 hours  
**Owner:** Improvement Lead (can delegate)

#### 1.1 Pull Request Audit

**Our Fork:**
```bash
# Fetch all open PRs
gh pr list --repo edithatogo/conductor-next \
  --state open \
  --json number,title,author,updatedAt,mergeable,isDraft \
  --limit 50

# Categorize PRs
# - Dependabot: author == "dependabot[bot]"
# - Security: title contains "security" or "vulnerability"
# - Community: all others
```

**Upstream:**
```bash
# Fetch all open upstream PRs
gh pr list --repo gemini-cli-extensions/conductor \
  --state open \
  --json number,title,author,updatedAt,labels \
  --limit 50

# Filter for high-impact PRs
# - Labels contain "feature", "breaking", "p0", "p1"
# - Our fork mentioned in comments
```

**Output:** PR audit spreadsheet or markdown table

---

#### 1.2 Security Scan

**Automated Scans:**
```bash
# Node.js projects
cd mcp-server && npm audit --json > ../security/npm-audit-mcp.json
cd conductor-vscode && npm audit --json > ../security/npm-audit-vscode.json

# Python projects
pip install safety pip-audit
safety check --json > security/pip-safety.json
pip-audit -r requirements.txt -f json > security/pip-audit.json

# GitHub Security
gh api /repos/edithatogo/conductor-next/code-scanning/alerts \
  --jq '.[] | {number, rule, severity, state}'
```

**Manual Review:**
- [ ] Check SECURITY.md exists
- [ ] Review .gitignore for sensitive files
- [ ] Check for hardcoded secrets
- [ ] Verify Dependabot alerts reviewed

**Output:** Security audit report

---

#### 1.3 Upstream Issues Analysis

**Fetch Issues:**
```bash
gh issue list --repo gemini-cli-extensions/conductor \
  --state open \
  --json number,title,labels,body,createdAt,updatedAt \
  --limit 100
```

**Categorization:**
```python
# Example categorization logic
categories = {
    'bugs': [],
    'features': [],
    'enhancements': [],
    'discussions': [],
    'p0_p1': []  # High priority
}

for issue in issues:
    labels = [l['name'] for l in issue['labels']]
    
    if 'p0' in labels or 'p1' in labels:
        categories['p0_p1'].append(issue)
    
    if 'bug' in labels:
        categories['bugs'].append(issue)
    elif 'feature' in labels:
        categories['features'].append(issue)
    # ... etc
```

**Relevance Scoring:**
For each issue, score relevance to fork:
- **5 - Critical:** Directly affects our differentiators
- **4 - High:** Important feature/bug we should address
- **3 - Medium:** Nice to have, but can wait
- **2 - Low:** Minor improvement
- **1 - None:** Not relevant to fork

**Output:** Prioritized issue list with adoption decisions

---

#### 1.4 Architecture Review

**Automated Metrics:**
```bash
# Count lines of code per module
find conductor-core -name "*.py" | xargs wc -l
find mcp-server -name "*.ts" | xargs wc -l
find mcp -name "*.ts" | xargs wc -l

# Dependency analysis
pipdeptree > deps-python.txt
cd mcp-server && npm list --depth=0 > deps-node.txt

# Test coverage
pytest --cov=conductor_core --cov-report=term-missing
```

**Manual Assessment:**
- [ ] Modules >1000 LOC consider for separation
- [ ] Circular dependencies identified
- [ ] Duplicate code detected
- [ ] API boundaries clear

**Output:** Architecture assessment report

---

### Phase 2: Analysis & Planning (Day 2-3)

**Duration:** 4-6 hours  
**Owner:** Improvement Lead

#### 2.1 Prioritization Matrix

Create 2x2 matrix:
```
Impact (1-5) vs Effort (XS-XL)

┌─────────────────┬──────────────────┬─────────────────┐
│                 │ High Impact (4-5)│ Low Impact (1-2)│
├─────────────────┼──────────────────┼─────────────────┤
│ Low Effort      │ DO NOW (P0)      │ SCHEDULE (P2)   │
│ (XS-S)          │                  │                  │
├─────────────────┼──────────────────┼─────────────────┤
│ High Effort     │ PLAN (P1)        │ DELEGATE/IGNORE │
│ (M-XL)          │                  │                  │
└─────────────────┴──────────────────┴─────────────────┘
```

**Populate with:**
- Dependabot PRs (usually P0)
- Security fixes (P0-P1)
- Upstream features to adopt (P1-P2)
- Architecture improvements (P1-P2)
- Ralph Mode enhancements (P1)

---

#### 2.2 Track Creation

**For P0 Items:**
```bash
# Create immediate action track
/conductor:newTrack "Merge Dependabot PRs and Security Fixes"

# Add to plan.md
- [ ] Review and merge PR #X
- [ ] Review and merge PR #Y
- [ ] Run security scan post-merge
```

**For P1-P2 Items:**
```bash
# Create comprehensive improvement track
/conductor:newTrack "Repository Improvement $(date +%Y%m%d)"

# Use improvement_track_template.md
# Populate spec.md and plan.md
```

---

### Phase 3: Implementation (Day 4-10)

**Duration:** 1 week (adjust based on scope)  
**Owner:** Improvement Lead + Ralph Mode (if enabled)

#### 3.1 Standard Implementation Workflow

Each task follows:

```
┌─────────────┐
│   SELECT    │ ← Select next task from plan.md
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  MARK [~]   │ ← Mark task in-progress
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ WRITE TESTS │ ← Red phase: failing tests
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  IMPLEMENT  │ ← Green phase: make tests pass
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   REFACTOR  │ ← Improve code quality
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   VERIFY    │ ← Run tests, check coverage
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   COMMIT    │ ← Commit with git note
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  UPDATE     │ ← Mark [x], add SHA
│   PLAN      │
└─────────────┘
```

#### 3.2 Ralph Mode Autonomous Implementation

If Ralph Mode enabled:

```bash
/conductor:implement --ralph \
  --max-iterations=10 \
  --completion-word=IMPROVEMENT_COMPLETE \
  --learning-enabled
```

**Ralph Mode will:**
1. Select tasks automatically
2. Write and run tests
3. Implement fixes
4. Log iterations to `.conductor/ralph-logs/`
5. Generate improvement suggestions
6. Report completion or blockers

---

### Phase 4: Verification (Day 11-12)

**Duration:** 4-6 hours  
**Owner:** Improvement Lead + Security Reviewer

#### 4.1 Quality Gates

**All Code:**
- [ ] Tests passing (100% core, 99% adapters)
- [ ] Coverage requirements met
- [ ] Static analysis clean
- [ ] No security vulnerabilities introduced

**Documentation:**
- [ ] README updated
- [ ] CHANGELOG updated
- [ ] API docs current
- [ ] Migration guides (if breaking changes)

**Security:**
- [ ] Final security scan clean
- [ ] No secrets committed
- [ ] Dependencies up-to-date

---

#### 4.2 Integration Testing

```bash
# Full integration test suite
./scripts/run_integration_tests.sh

# Smoke test
python scripts/smoke_test.py

# Cross-platform validation (if CI supports)
# Check GitHub Actions results
```

---

### Phase 5: Retrospective & Learning (Day 13-14)

**Duration:** 2-3 hours  
**Owner:** Entire team

#### 5.1 Retrospective Meeting

**Agenda:**
1. Review what was accomplished
2. Identify what went well
3. Identify improvement opportunities
4. Plan next cycle

**Template:**
```markdown
## Retrospective: {{DATE}}

### What Went Well
- {{Item 1}}
- {{Item 2}}

### What Could Be Better
- {{Item 1}}
- {{Item 2}}

### Action Items
- [ ] {{Action 1}}
- [ ] {{Action 2}}

### Metrics
- PRs merged: {{COUNT}}
- Security issues fixed: {{COUNT}}
- Upstream issues adopted: {{COUNT}}
- Ralph Mode iterations: {{COUNT}}
- Pattern improvements generated: {{COUNT}}
```

---

#### 5.2 Ralph Mode Learning Analysis

If Ralph Mode enabled:

```python
from conductor.ralph.pattern_analyzer import PatternAnalyzer
from conductor.ralph.improvement_generator import ImprovementGenerator

# Analyze patterns
analyzer = PatternAnalyzer(logs_path='.conductor/ralph-logs/')
recurring_failures = analyzer.find_recurring_failures(min_occurrences=3)
success_patterns = analyzer.get_success_patterns()

# Generate improvements
generator = ImprovementGenerator(analyzer)
improvements = generator.generate_improvements()

# Report
print(f"Recurring failures: {len(recurring_failures)}")
print(f"Success patterns: {success_patterns}")
print(f"Improvements to implement: {len(improvements)}")
```

**Output:**
- List of recurring issues to address
- Success patterns to reinforce
- Automated improvement tracks to create

---

#### 5.3 Update Templates

Based on learnings:
- [ ] Update `improvement_track_template.md`
- [ ] Update `improvement_workflow.md`
- [ ] Update checklists
- [ ] Update automation scripts

---

## Automation Opportunities

### 1. Automated Data Collection

**Script:** `scripts/collect_improvement_data.py`

```python
#!/usr/bin/env python3
"""Collect data for repository improvement cycle."""

import json
from datetime import datetime
from pathlib import Path
import subprocess

def run_gh_command(cmd: str) -> list:
    """Run GitHub CLI command and parse JSON output."""
    result = subprocess.run(
        f"gh {cmd} --json number,title,author,updatedAt,labels",
        shell=True,
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout) if result.stdout else []

def collect_data():
    """Collect all improvement data."""
    output_dir = Path('.conductor/improvement-data')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Our PRs
    our_prs = run_gh_command(
        "pr list --repo edithatogo/conductor-next --state open"
    )
    with open(output_dir / 'our-prs.json', 'w') as f:
        json.dump(our_prs, f, indent=2)
    
    # Upstream PRs
    upstream_prs = run_gh_command(
        "pr list --repo gemini-cli-extensions/conductor --state open"
    )
    with open(output_dir / 'upstream-prs.json', 'w') as f:
        json.dump(upstream_prs, f, indent=2)
    
    # Upstream issues
    upstream_issues = run_gh_command(
        "issue list --repo gemini-cli-extensions/conductor --state open"
    )
    with open(output_dir / 'upstream-issues.json', 'w') as f:
        json.dump(upstream_issues, f, indent=2)
    
    print(f"✓ Collected data for {len(our_prs)} PRs, "
          f"{len(upstream_prs)} upstream PRs, "
          f"{len(upstream_issues)} upstream issues")

if __name__ == '__main__':
    collect_data()
```

---

### 2. Automated Security Scan

**Script:** `scripts/security_scan.py`

```python
#!/usr/bin/env python3
"""Run comprehensive security scans."""

import subprocess
import json
from pathlib import Path

def npm_audit(path: Path) -> dict:
    """Run npm audit."""
    result = subprocess.run(
        ['npm', 'audit', '--json'],
        cwd=path,
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout) if result.stdout else {}

def pip_safety() -> list:
    """Run safety check."""
    result = subprocess.run(
        ['safety', 'check', '--json'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout) if result.stdout else []

def generate_report():
    """Generate security report."""
    report = {
        'npm': {},
        'pip': [],
        'github_alerts': []
    }
    
    # NPM audits
    for dir in ['mcp-server', 'conductor-vscode', 'mcp']:
        report['npm'][dir] = npm_audit(Path(dir))
    
    # PIP safety
    report['pip'] = pip_safety()
    
    # GitHub alerts
    # ... API call
    
    # Save report
    with open('.conductor/security-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    total_vulns = sum(
        len(r.get('vulnerabilities', []))
        for r in report['npm'].values()
    ) + len(report['pip'])
    
    print(f"Security scan complete: {total_vulns} vulnerabilities found")
    return total_vulns == 0

if __name__ == '__main__':
    success = generate_report()
    exit(0 if success else 1)
```

---

### 3. Scheduled GitHub Action

**File:** `.github/workflows/monthly-improvement.yml`

```yaml
name: Monthly Repository Improvement

on:
  schedule:
    # First Monday of every month at 09:00 UTC
    - cron: '0 9 1-7 * 1'
  workflow_dispatch:
    inputs:
      focus_area:
        description: 'Specific focus area (optional)'
        required: false
        default: 'all'

jobs:
  collect-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install PyGithub requests
      
      - name: Collect improvement data
        run: |
          python scripts/collect_improvement_data.py
      
      - name: Run security scan
        run: |
          python scripts/security_scan.py
      
      - name: Upload data artifact
        uses: actions/upload-artifact@v4
        with:
          name: improvement-data
          path: .conductor/improvement-data/
          retention-days: 30
      
      - name: Create improvement track
        if: success()
        run: |
          # Parse data and create track
          python scripts/create_improvement_track.py \
            --data .conductor/improvement-data \
            --output conductor/tracks/
      
      - name: Notify team
        if: success()
        run: |
          echo "::notice::Monthly improvement track created. Review at: ${{ github.server_url }}/${{ github.repository }}/tree/main/conductor/tracks/"
```

---

## Metrics & KPIs

Track these metrics each cycle:

| Metric | Target | Measurement |
|--------|--------|-------------|
| PRs Merged | 100% of Dependabot | Count / Total |
| Security Vulnerabilities | 0 critical, <5 low | Security scan |
| Upstream Issues Adopted | ≥2 per cycle | Count |
| Ralph Mode Iterations | ≥10 per track | Iteration logs |
| Pattern Improvements | ≥1 per cycle | Improvement generator |
| Test Coverage | >95% core, >99% adapters | Coverage reports |
| CI Duration | <15 minutes | GitHub Actions |
| Technical Debt Ratio | <10% of tasks | Task categorization |

---

## Continuous Improvement

This workflow itself should improve over time:

1. **After Each Cycle:**
   - Update templates based on learnings
   - Refine automation scripts
   - Adjust time estimates

2. **Quarterly Review:**
   - Assess workflow effectiveness
   - Incorporate new best practices
   - Update Ralph Mode integration

3. **Annual Audit:**
   - Complete workflow redesign if needed
   - Align with industry standards
   - Benchmark against similar projects

---

## Appendix: Quick Reference

### One-Command Improvement Start

```bash
# Run this to start monthly improvement cycle
./scripts/start_improvement_cycle.sh
```

**Script:** `scripts/start_improvement_cycle.sh`
```bash
#!/bin/bash
set -e

echo "🚀 Starting monthly repository improvement cycle..."

# Collect data
python scripts/collect_improvement_data.py

# Security scan
python scripts/security_scan.py

# Create track
python scripts/create_improvement_track.py

echo "✅ Improvement cycle started!"
echo "📋 Review track at: conductor/tracks/repo_improvement_$(date +%Y%m%d)/"
echo "🎯 Start implementation with: /conductor:implement"
```

---

**Document Control:**
- **Version:** 1.0
- **Effective:** March 3, 2026
- **Next Review:** April 3, 2026
- **Owner:** Repository Maintainer
- **Approvers:** [List approvers]
