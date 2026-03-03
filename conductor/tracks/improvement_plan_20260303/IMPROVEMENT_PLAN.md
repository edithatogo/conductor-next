# Conductor-Next Improvement Plan

**Track ID:** `improvement_plan_20260303`  
**Created:** March 3, 2026  
**Status:** Proposal  
**Author:** AI Agent (via GitHub Research & Analysis)

---

## Executive Summary

This document presents a comprehensive improvement plan for the conductor-next repository, based on analysis of:
- 9 open Dependabot PRs requiring review and merge
- 12 upstream issues from gemini-cli-extensions/conductor
- 14 upstream PRs (including our major PR #93 with 83 commits)
- Current repository architecture and skill design
- CI/CD workflows and automation opportunities
- Ralph Mode integration and self-improvement capabilities

**Key Findings:**
- ✅ **Security Posture:** Clean but needs SECURITY.md file
- ⚠️ **Technical Debt:** 9 dependency PRs pending merge
- 🎯 **Strategic Opportunity:** PR #93 (our multi-VCS PR) defines fork's value proposition
- 🔄 **Ralph Mode:** Present but could be enhanced for autonomous self-improvement
- 📦 **Architecture:** Skills may need separation into submodules

---

## 1. IMMEDIATE ACTIONS (Week 1)

### 1.1 Merge Dependabot PRs (#4-12)

**Priority:** HIGH  
**Effort:** LOW (2-3 hours)  
**Risk:** LOW

**Action Items:**
1. Review and merge all 9 dependency update PRs:
   - PR #12: minimatch 3.1.2 → 3.1.5 (security patch) - **MEDIUM PRIORITY**
   - PR #11: rollup 4.57.0 → 4.59.0 (minor) - LOW PRIORITY
   - PR #10: hono 4.11.7 → 4.12.2 (minor) - MEDIUM PRIORITY
   - PR #9: qs 6.14.1 → 6.15.0 (patch) - LOW PRIORITY
   - PR #8: ajv 8.17.1 → 8.18.0 (patch) - LOW PRIORITY
   - PR #7: hono 4.11.7 → 4.12.0 (minor) - LOW PRIORITY
   - PR #6: esbuild + vitest (dev deps) - LOW PRIORITY
   - PR #5: @modelcontextprotocol/sdk 1.25.3 → 1.26.0 - **MEDIUM PRIORITY**
   - PR #4: qs 6.14.1 → 6.15.0 (patch) - LOW PRIORITY

2. **Batch Merge Strategy:**
   ```bash
   # Checkout main and pull all PRs
   git checkout main
   git pull origin main
   
   # Test each dependency update
   cd mcp-server && npm install && npm test
   cd ../conductor-vscode && npm install && npm test
   cd ../mcp && npm install && npm test
   
   # Merge in batches by directory
   git merge --no-ff dependabot/npm_and_yarn/mcp-server/hono-4.12.2
   git merge --no-ff dependabot/npm_and_yarn/mcp-server/ajv-8.18.0
   # ... etc
   ```

3. **Automation Opportunity:** Enable Dependabot auto-merge for patch/minor updates with passing CI

---

### 1.2 Create SECURITY.md

**Priority:** HIGH  
**Effort:** LOW (30 minutes)  
**Risk:** NONE

**Template:**
```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| < latest | :x:                |

## Reporting a Vulnerability

We take the security of Conductor seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to [security@edithatogo.com](mailto:security@edithatogo.com) with the following information:

1. Description of the vulnerability
2. Steps to reproduce the issue
3. Potential impact
4. Suggested fix (if any)

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

After the initial reply to your report, we will send you regular updates about the progress of our fix and full announcement.

## Security Best Practices

When using Conductor:

1. Never commit sensitive information (API keys, tokens, passwords)
2. Review all generated code before execution
3. Keep dependencies updated
4. Use in secure environments only

## Known Security Considerations

- Conductor uses AI-generated code - always review before production use
- Token consumption may expose project context to AI services
- Git operations should be reviewed before execution

## Acknowledgments

We would like to thank the following for their contributions to our security:

- [List of security researchers who reported issues]

---

**Last Updated:** March 3, 2026
```

---

### 1.3 Monitor PR #93 (Our Multi-VCS Contribution)

**Priority:** CRITICAL  
**Effort:** ONGOING  
**Risk:** MEDIUM (merge conflicts if upstream moves fast)

**Context:**
PR #93 is our major architectural contribution to upstream with 83 commits, including:
- Unified Core Architecture (conductor-core)
- Multi-VCS Support (Git, JJ, Piper, Mercurial)
- Enhanced Platform Integration (AIX, SkillShare)
- 100% test coverage for conductor-core
- Windows compatibility fixes
- New infrastructure (universal installer, sync bot)

**Action Items:**
1. **Engage with Reviewers:**
   - Tag Google team members: @mshanware @sherzat @nathenharvey @moisgobg @john.mcdole
   - Respond to any feedback within 24 hours
   - Proactively request review status

2. **Conflict Prevention:**
   ```bash
   # Daily rebase to stay current with upstream
   git fetch upstream
   git rebase upstream/main
   
   # Run tests after rebase
   ./scripts/run_all_tests.sh
   ```

3. **Documentation:**
   - Update PR description with latest test results
   - Add migration guide for existing users
   - Create demo video showing multi-VCS features

---

## 2. SHORT-TERM IMPROVEMENTS (Weeks 2-3)

### 2.1 Adopt Artifact Inference Setup (Upstream PR #137)

**Priority:** HIGH  
**Effort:** MEDIUM (4-6 hours)  
**Impact:** MAJOR setup architecture improvement

**What is PR #137?**
Replaces brittle `setup_state.json` with declarative "Artifact Audit" approach:
- State inference via Priority Table mapping artifacts to setup sections
- Refined Greenfield/Brownfield detection (Conductor-aware)
- Fast-forward logic for context establishment
- Self-healing: cleanup step for interrupted track generations
- Token efficiency: reduced prompt logic, eliminated redundant file writes

**Adoption Strategy:**

**Option A: Wait for Upstream Merge** (Recommended)
- Monitor PR #137 progress
- Review hminooei's feedback: "Is it possible that a .md file exists but it's incomplete?"
- Test thoroughly once merged upstream
- Merge into fork with proper testing

**Option B: Early Adoption** (If urgent)
```bash
# Create feature branch
git checkout -b feature/artifact-inference-setup

# Cherry-pick or manually implement PR #137 changes
# Key files to modify:
# - conductor-core/src/setup.py
# - conductor-core/src/state_inference.py (new)
# - conductor-core/src/artifact_audit.py (new)

# Test scenarios:
# 1. Fresh greenfield project
# 2. Brownfield project without Conductor
# 3. Brownfield project with partial Conductor setup
# 4. Interrupted setup recovery
```

**Testing Checklist:**
- [ ] Greenfield detection works correctly
- [ ] Brownfield detection ignores `conductor/` directory
- [ ] Resume from interrupted setup works
- [ ] Token usage reduced by >20%
- [ ] Self-healing cleans up partial track generations

---

### 2.2 Cross-Platform Compatibility Fixes

**Priority:** HIGH  
**Effort:** MEDIUM (6-8 hours)  
**Impact:** Critical for macOS/Linux users

**Issues to Address:**

#### Issue #120: Linux Template Finding Bug
**Symptom:** Templates cannot be found on Linux  
**Root Cause:** Path resolution differences between Windows/Unix

**Fix Strategy:**
```python
# Current (broken on Linux):
template_path = f"{base_dir}\\templates\\{template_name}"

# Fixed (cross-platform):
from pathlib import Path
template_path = Path(base_dir) / "templates" / template_name

# Or use os.path:
import os
template_path = os.path.join(base_dir, "templates", template_name)
```

#### Upstream PR #56: macOS `ls -I` Incompatibility
**Problem:** `ls -lR -I 'node_modules'` fails on macOS/BSD (no -I flag)  
**Impact:** node_modules scanned, causing API token limit errors

**Solution from PR #56:**
```bash
# Instead of:
ls -lR -I 'node_modules'

# Use cross-platform find:
find . -type d -name 'node_modules' -prune -o -type f -print | head -200

# Or Git-aware approach (if Git project):
git ls-files --exclude-standard -co | xargs -n 1 dirname | sort -u
```

**Implementation Plan:**
1. Audit all shell commands in:
   - `conductor-core/src/`
   - `conductor-gemini/src/`
   - `scripts/`
   
2. Replace non-portable commands:
   ```python
   # Use subprocess with shell=True only when necessary
   # Prefer Python pathlib and os module
   from pathlib import Path
   import os
   
   # Instead of shell pipes, use Python:
   files = [f for f in Path('.').rglob('*') 
            if not any(ignore in str(f) for ignore in ['node_modules', '__pycache__', '.git'])]
   ```

3. Add CI matrix for macOS and Linux:
   ```yaml
   # .github/workflows/ci.yml
   strategy:
     matrix:
       os: [ubuntu-latest, macos-latest, windows-latest]
       python-version: ['3.9', '3.10', '3.11', '3.12']
   ```

---

### 2.3 Multi-Tool Support Expansion

**Priority:** MEDIUM  
**Effort:** MEDIUM (8-10 hours)  
**Impact:** Expands user base significantly

**Current State:**
- ✅ Gemini CLI: Fully supported
- ✅ Qwen Code: Supported via `qwen-extension.json` (PR #87 upstream)
- ✅ VS Code: Supported via VSIX
- ⚠️ Claude Code: Supported via portable skills (needs review)
- ⚠️ AIX/SkillShare: Mentioned but needs validation

**Action Items:**

#### 2.3.1 Adopt PR #87 Approach (Qwen Compatibility)
**What:** Add tool-specific configuration files for broader compatibility

**Implementation:**
```json
// qwen-extension.json (already present ✅)
{
  "name": "conductor",
  "version": "1.0.0",
  "description": "Context-Driven Development for Qwen Code"
}

// Consider adding:
// claude-code.json (for Claude Code marketplace)
// codex-extension.json (for Codex CLI)
```

#### 2.3.2 Audit Claude Code Integration
```bash
# Check current state:
ls -la .claude/commands/
ls -la .claude/skills/

# Verify sync with core templates:
python scripts/sync_all.py --target claude

# Test installation:
./skill/scripts/install.sh --target claude
```

#### 2.3.3 Add Configuration for Missing Tools
**Priority Order:**
1. **GitHub Copilot Chat** (high user base)
2. **Codex CLI** (growing adoption)
3. **AIX** (niche but loyal users)
4. **SkillShare** (emerging platform)

**Template:**
```markdown
# ~/.config/github-copilot/conductor.md

## /conductor-setup
Initialize Conductor in your project...

## /conductor-newtrack
Create a new feature/bug track...
```

---

### 2.4 Configurable Storage Directory (Issue #117)

**Priority:** MEDIUM  
**Effort:** LOW-MEDIUM (3-4 hours)  
**Impact:** Better organization, user experience

**Current Problem:**
Multiple AI extensions create directories in project root, causing clutter:
```
project-root/
├── conductor/
├── .gemini/
├── .claude/
├── .codex/
└── .agent/
```

**User Request:**
Allow configuration to use `.agents/conductor` or similar hidden directory.

**Implementation:**

#### Step 1: Add Configuration Option
```python
# conductor-core/src/config.py
from pathlib import Path
import os

class ConductorConfig:
    def __init__(self):
        # Check environment variable first
        custom_dir = os.environ.get('CONDUCTOR_DIR')
        
        if custom_dir:
            self.base_dir = Path(custom_dir)
        else:
            # Default to project root for backward compatibility
            self.base_dir = Path.cwd() / 'conductor'
    
    @property
    def tracks_dir(self):
        return self.base_dir / 'tracks'
    
    @property
    def metadata_file(self):
        return self.base_dir / 'metadata.jsonl'
```

#### Step 2: Update Setup Command
```toml
# commands/conductor/setup.toml

[setup_options]
storage_location = { type = "choice", choices = ["root", "hidden", "custom"], default = "root" }

# If "hidden": use .conductor/
# If "custom": prompt for path
# If "root": use conductor/ (default)
```

#### Step 3: Migration Script
```python
# scripts/migrate_storage.py
#!/usr/bin/env python3
"""Migrate conductor directory to new location."""

import shutil
from pathlib import Path

def migrate(old_path: Path, new_path: Path):
    """Move conductor files to new location."""
    if old_path.exists():
        new_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_path), str(new_path))
        print(f"✓ Migrated {old_path} → {new_path}")
```

#### Step 4: Documentation Update
Update README.md, INSTALL.md with new configuration option.

---

## 3. MEDIUM-TERM ENHANCEMENTS (Weeks 4-6)

### 3.1 Ralph Mode Enhancement for Self-Improvement

**Priority:** HIGH  
**Effort:** HIGH (12-16 hours)  
**Impact:** Autonomous self-improvement capability

**Current State:**
Ralph Mode exists in `hooks/ralph-mode/directive.md` with basic Red-Green-Refactor loop.

**Limitations:**
- No learning from past iterations
- No pattern recognition for recurring issues
- No integration with upstream issue tracking
- No automated improvement suggestions

**Enhanced Ralph Mode Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                 RALPH MODE 2.0                          │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐ │
│  │   Context    │    │   Execution  │    │ Learning │ │
│  │   Analyzer   │───▶│   Engine     │───▶│  System  │ │
│  └──────────────┘    └──────────────┘    └──────────┘ │
│         ▲                   │                  │       │
│         │                   ▼                  │       │
│         │          ┌──────────────┐           │       │
│         └──────────│  Improvement │◀──────────┘       │
│                    │  Generator   │                   │
│                    └──────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

#### 3.1.1 Learning System Components

**Component 1: Iteration Logger**
```python
# conductor-core/src/ralph/iteration_logger.py
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json

@dataclass
class RalphIteration:
    track_id: str
    task_id: str
    cycle_number: int
    status: str  # 'SUCCESS', 'FAILURE', 'STUCK'
    error_type: str | None
    error_message: str | None
    tests_written: int
    code_changes: list[str]
    duration_seconds: float
    timestamp: datetime

class IterationLogger:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def log_iteration(self, iteration: RalphIteration):
        """Log iteration to JSONL file."""
        log_file = self.storage_path / f"{iteration.track_id}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(iteration.__dict__) + '\n')
    
    def get_track_history(self, track_id: str) -> list[RalphIteration]:
        """Retrieve all iterations for a track."""
        log_file = self.storage_path / f"{track_id}.jsonl"
        if not log_file.exists():
            return []
        
        iterations = []
        with open(log_file, 'r') as f:
            for line in f:
                data = json.loads(line)
                iterations.append(RalphIteration(**data))
        return iterations
```

**Component 2: Pattern Recognition**
```python
# conductor-core/src/ralph/pattern_analyzer.py
from collections import Counter
from .iteration_logger import IterationLogger

class PatternAnalyzer:
    def __init__(self, logger: IterationLogger):
        self.logger = logger
    
    def find_recurring_failures(self, min_occurrences: int = 3) -> list[dict]:
        """Find error patterns that occur multiple times."""
        all_iterations = []
        for log_file in self.logger.storage_path.glob('*.jsonl'):
            track_id = log_file.stem
            all_iterations.extend(self.logger.get_track_history(track_id))
        
        # Count error types
        error_counter = Counter(
            i.error_type for i in all_iterations 
            if i.status == 'FAILURE' and i.error_type
        )
        
        # Return recurring patterns
        return [
            {'error_type': error_type, 'count': count}
            for error_type, count in error_counter.items()
            if count >= min_occurrences
        ]
    
    def get_success_patterns(self) -> list[dict]:
        """Find patterns in successful iterations."""
        successful = [
            i for log_file in self.logger.storage_path.glob('*.jsonl')
            for i in self.logger.get_track_history(log_file.stem)
            if i.status == 'SUCCESS'
        ]
        
        # Analyze common characteristics
        return {
            'avg_cycles_per_task': sum(i.cycle_number for i in successful) / len(successful),
            'avg_tests_per_task': sum(i.tests_written for i in successful) / len(successful),
            'common_error_types_resolved': Counter(
                i.error_type for i in successful if i.cycle_number > 1
            )
        }
```

**Component 3: Improvement Generator**
```python
# conductor-core/src/ralph/improvement_generator.py
from pathlib import Path
from .pattern_analyzer import PatternAnalyzer

class ImprovementGenerator:
    def __init__(self, analyzer: PatternAnalyzer):
        self.analyzer = analyzer
    
    def generate_improvements(self) -> list[dict]:
        """Generate improvement suggestions based on patterns."""
        improvements = []
        
        # Check for recurring failures
        recurring = self.analyzer.find_recurring_failures()
        for pattern in recurring:
            improvements.append({
                'type': 'PREVENTIVE_MEASURE',
                'priority': 'HIGH',
                'description': f"Add handling for recurring error: {pattern['error_type']}",
                'occurrences': pattern['count'],
                'suggested_action': f"Create template/test for {pattern['error_type']}"
            })
        
        # Check for efficiency improvements
        success_patterns = self.analyzer.get_success_patterns()
        if success_patterns['avg_cycles_per_task'] > 3:
            improvements.append({
                'type': 'EFFICIENCY',
                'priority': 'MEDIUM',
                'description': "High iteration count detected",
                'metric': f"{success_patterns['avg_cycles_per_task']:.1f} cycles/task",
                'suggested_action': "Improve initial test generation or code templates"
            })
        
        return improvements
    
    def create_improvement_track(self, improvement: dict) -> Path:
        """Create a new Conductor track for implementing improvement."""
        from conductor_core.newtrack import create_track
        
        track = create_track(
            title=f"Ralph Improvement: {improvement['description']}",
            description=f"""
Automated improvement suggestion from Ralph Mode analysis.

**Type:** {improvement['type']}
**Priority:** {improvement['priority']}
**Occurrences:** {improvement.get('occurrences', 'N/A')}

**Suggested Action:**
{improvement['suggested_action']}

**Implementation Plan:**
1. Analyze current implementation
2. Design improvement
3. Write tests
4. Implement
5. Verify with Ralph Mode
"""
        )
        return track
```

#### 3.1.2 Integration with Upstream Issues

**Component 4: Upstream Issue Monitor**
```python
# conductor-core/src/ralph/upstream_monitor.py
import requests
from typing import Optional

class UpstreamMonitor:
    def __init__(self, repo: str = "gemini-cli-extensions/conductor"):
        self.repo = repo
        self.api_base = f"https://api.github.com/repos/{repo}"
    
    def get_open_issues(self, labels: Optional[list[str]] = None) -> list[dict]:
        """Fetch open issues from upstream."""
        url = f"{self.api_base}/issues"
        params = {'state': 'open', 'per_page': 100}
        if labels:
            params['labels'] = ','.join(labels)
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def find_relevant_issues(self, error_type: str) -> list[dict]:
        """Find upstream issues related to specific error type."""
        issues = self.get_open_issues()
        
        # Simple keyword matching (could use embeddings for better matching)
        keywords = error_type.lower().split()
        relevant = []
        
        for issue in issues:
            title = issue['title'].lower()
            body = issue['body'].lower() if issue['body'] else ''
            
            if any(keyword in title or keyword in body for keyword in keywords):
                relevant.append(issue)
        
        return relevant
    
    def create_issue_report(self) -> dict:
        """Generate report of relevant upstream issues."""
        issues_by_label = {}
        
        for label in ['bug', 'enhancement', 'feature request']:
            issues = self.get_open_issues(labels=[label])
            issues_by_label[label] = issues
        
        return {
            'total_open_issues': sum(len(v) for v in issues_by_label.values()),
            'by_label': issues_by_label,
            'high_priority': [
                i for i in issues_by_label.get('bug', [])
                if 'p1' in [l['name'] for l in i['labels']]
            ]
        }
```

#### 3.1.3 Enhanced Ralph Mode Directive

**Updated `hooks/ralph-mode/directive.md`:**
```markdown
## 🔴 RALPH MODE 2.0: AUTONOMOUS SELF-IMPROVEMENT

**ATTENTION:** Announce verbatim
> 🔁 Operating in **RALPH MODE 2.0** with learning enabled.

**ENHANCED INSTRUCTIONS:**

1. **Initialization:**
   - Initialize Iteration Logger at `.conductor/ralph-logs/`
   - Load Pattern Analyzer
   - Check for improvement suggestions from previous runs

2. **Execute Standard Protocol:** Follow Steps 3.1, 3.2, 3.3, 3.5 from "TRACK IMPLEMENTATION"

3. **Enhanced Autonomous Cycle:**
   For each task:
   a. **RED:** Write failing tests
   b. **GREEN:** Implement code
   c. **VERIFY:** Run tests
      - IF FAIL:
        1. Log failure with error type
        2. Check Pattern Analyzer for similar past failures
        3. Apply learned solutions if available
        4. Attempt fix (max 3 iterations)
        5. If still failing → call 'ralph_end' with status='FAILURE'
   d. **LEARN:** After each task:
      - Log iteration to `.conductor/ralph-logs/{track_id}.jsonl`
      - Update success/failure patterns
   e. **PASS:** Mark task [x] and commit

4. **End-of-Track Analysis:**
   After completing track:
   a. Run Pattern Analyzer on accumulated logs
   b. Generate Improvement Report
   c. If improvements found:
      - Present to user
      - Offer to create improvement tracks
   d. Check upstream for relevant issues
   e. Call 'ralph_end' with status='SUCCESS' + analysis summary

5. **Self-Improvement Loop:**
   Weekly (or every 10 tracks):
   a. Aggregate all iteration logs
   b. Identify top 3 recurring issues
   c. Create improvement tracks automatically
   d. Prioritize in next implementation cycle

**COMPLETION CRITERIA:**
- All tests pass
- All tasks marked [x]
- Improvement report generated
- User approves analysis

**SAFETY GUARDS:**
- Max 10 iterations per task
- Auto-stop on 3 consecutive failures
- Human review required for code changes >500 lines
```

---

### 3.2 Skill/Submodule Separation Analysis

**Priority:** MEDIUM  
**Effort:** MEDIUM (6-8 hours for analysis, more for implementation)  
**Impact:** Better modularity, maintainability

**Current Structure:**
```
conductor-next/
├── conductor-core/          # ✅ Good: Platform-agnostic core
├── conductor-gemini/        # ✅ Good: Adapter pattern
├── conductor-vscode/        # ✅ Good: VS Code extension
├── mcp/                     # ⚠️ Question: Separate repo?
├── mcp-server/              # ⚠️ Question: Separate repo?
├── skills/                  # ⚠️ Question: Keep or separate?
│   └── conductor/
└── hooks/                   # ⚠️ Question: Keep or separate?
    └── ralph-mode/
```

#### Analysis Criteria:

**Should SEPARATE if:**
- ✅ Has independent user base
- ✅ Can function standalone
- ✅ Different release cycle
- ✅ Different dependency tree
- ✅ Large codebase (>1000 LOC)

**Should KEEP in monorepo if:**
- ✅ Tightly coupled with core
- ✅ Shares release cycle
- ✅ Small (<500 LOC)
- ✅ Core functionality

#### Recommendations:

**1. MCP Server → Separate Repository**
```
Reasoning:
- ✅ Independent functionality (MCP protocol implementation)
- ✅ Different tech stack (TypeScript vs Python core)
- ✅ Separate release cycle
- ✅ Can be used by other projects
- ✅ Growing codebase

Action:
1. Create github.com/edithatogo/conductor-mcp
2. Move mcp/ and mcp-server/ directories
3. Add as git submodule or keep as optional dependency
4. Update main repo README with link
```

**2. Ralph Mode → Keep in Core**
```
Reasoning:
- ❌ Tightly integrated with implement command
- ❌ Core workflow functionality
- ❌ Small codebase
- ✅ Part of Conductor value proposition

Action: Keep in conductor-core/src/ralph/
```

**3. Skills Directory → Keep but Reorganize**
```
Reasoning:
- ✅ Platform-specific artifacts
- ❌ Cannot function without core
- ✅ Part of distribution

Action:
1. Keep in main repo
2. Reorganize by platform:
   skills/
   ├── gemini/
   ├── claude/
   ├── qwen/
   └── vscode/
3. Automate sync with scripts/sync_all.py
```

**4. Hooks Directory → Integrate into Core**
```
Reasoning:
- ✅ Workflow extensions
- ❌ Cannot function standalone
- ✅ Part of core behavior

Action:
1. Move to conductor-core/src/hooks/
2. Make pluggable via configuration
3. Document hook API
```

---

### 3.3 CI/CD Improvements

**Priority:** MEDIUM  
**Effort:** MEDIUM (8-10 hours)  
**Impact:** Better reliability, faster feedback

**Current State:**
- ✅ Basic CI with Python matrix (3.9-3.12)
- ✅ Test coverage requirements (100% core, 99% gemini)
- ✅ Static analysis (ruff, mypy)
- ✅ Artifact building (core, VSIX)
- ✅ Upstream sync (daily)
- ❌ No macOS testing
- ❌ No Windows testing (despite Windows fixes in PR #93)
- ❌ No security scanning
- ❌ No performance benchmarks
- ❌ No integration tests

#### Improvements:

**1. Add Platform Matrix**
```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']
        exclude:
          # Skip some combinations to reduce CI time
          - os: macos-latest
            python-version: '3.9'
          - os: windows-latest
            python-version: '3.9'
```

**2. Add Security Scanning**
```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install safety
        run: pip install safety bandit
      
      - name: Check Python dependencies
        run: safety check
      
      - name: Run Bandit security lint
        run: bandit -r conductor-core/src conductor-gemini/src
      
      - name: npm audit
        run: |
          cd mcp-server && npm audit
          cd ../conductor-vscode && npm audit
```

**3. Add Integration Tests**
```yaml
# .github/workflows/integration.yml
name: Integration Tests

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 6 * * *'  # Daily

jobs:
  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
      
      - name: Install Conductor
        run: pip install -e ./conductor-core -e ./conductor-gemini
      
      - name: Create test project
        run: |
          mkdir test-project && cd test-project
          git init
          /conductor:setup --non-interactive
      
      - name: Create track
        run: |
          cd test-project
          /conductor:newtrack "Test feature"
      
      - name: Implement track (Ralph Mode)
        run: |
          cd test-project
          /conductor:implement --ralph --max-iterations=5
      
      - name: Verify results
        run: |
          cd test-project
          python -c "from conductor.tracks import *; assert all_tracks_complete()"
```

**4. Add Performance Benchmarks**
```yaml
# .github/workflows/benchmarks.yml
name: Performance Benchmarks

on:
  pull_request:
    branches: [main]
    paths:
      - 'conductor-core/**'
      - 'conductor-gemini/**'

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run benchmarks
        run: |
          cd conductor-core
          pytest --benchmark-only --benchmark-json=benchmark.json
      
      - name: Store benchmark result
        uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: 'pytest'
          output-file-path: conductor-core/benchmark.json
          github-token: ${{ secrets.GITHUB_TOKEN }}
          auto-push: true
```

**5. Add Automated Release**
```yaml
# Already have release-please.yml ✅
# Enhance with:
# - Automated changelog generation
# - Semantic versioning enforcement
# - Pre-release validation
# - Asset upload to GitHub Releases
```

---

## 4. LONG-TERM STRATEGIC INITIATIVES (Months 2-3)

### 4.1 Accessibility Integration (Issue #130)

**Priority:** MEDIUM  
**Effort:** HIGH (16-20 hours)  
**Impact:** Social responsibility, broader user base

**Implementation:**
1. Add accessibility checks to UI app templates
2. Integrate axe-core or similar tools
3. Create accessibility spec templates
4. Add to workflow.md for UI projects

---

### 4.2 Plan Mode Strategy (Issues #121, #122)

**Priority:** MEDIUM  
**Effort:** MEDIUM (8-10 hours)  
**Impact:** UX with Gemini CLI

**Decision Points:**
- Integrate with Gemini CLI plan mode?
- Maintain separation?
- Implement warning hooks (PR #124)?

**Recommendation:**
Wait for upstream resolution, then adopt based on community feedback.

---

### 4.3 Documentation Excellence

**Priority:** LOW-MEDIUM  
**Effort:** ONGOING  
**Impact:** User adoption, contributor onboarding

**Action Items:**
1. Video tutorials for each command
2. Interactive demo environment
3. Migration guides from other tools
4. API documentation for conductor-core
5. Contributor guide with development setup

---

## 5. SUCCESS METRICS

### Week 1 Metrics:
- [ ] All 9 Dependabot PRs merged
- [ ] SECURITY.md created and published
- [ ] PR #93 engagement: at least 1 reviewer engaged

### Week 2-3 Metrics:
- [ ] Artifact Inference Setup tested and benchmarked
- [ ] Cross-platform CI matrix passing on all 3 platforms
- [ ] Multi-tool configs added for 2+ new platforms

### Month 1 Metrics:
- [ ] Ralph Mode 2.0 implemented with learning system
- [ ] First automated improvement track created
- [ ] MCP server separation completed
- [ ] Security scanning integrated into CI

### Month 2-3 Metrics:
- [ ] 10+ tracks completed with Ralph Mode 2.0
- [ ] Pattern database with 100+ iterations logged
- [ ] 3+ recurring issues identified and fixed
- [ ] Upstream issue integration working
- [ ] Accessibility checks in UI templates

---

## 6. RISK ASSESSMENT

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| PR #93 merge conflicts | MEDIUM | HIGH | Daily rebases, frequent communication |
| Upstream adopts our features | MEDIUM | MEDIUM | Maintain differentiation via Ralph Mode 2.0 |
| Ralph Mode learning overhead | LOW | LOW | Optional feature, disabled by default |
| MCP separation breaks deps | LOW | MEDIUM | Thorough testing, version pinning |
| Cross-platform CI increases cost | HIGH | LOW | Optimize matrix, use caching |

---

## 7. NEXT STEPS

### Immediate (This Week):
1. ✅ Merge Dependabot PRs #4-12
2. ✅ Create SECURITY.md
3. ✅ Engage with PR #93 reviewers

### Week 2:
4. ⏳ Review and adopt PR #137 (Artifact Inference)
5. ⏳ Fix cross-platform compatibility issues
6. ⏳ Add multi-tool configurations

### Week 3-4:
7. ⏳ Implement Ralph Mode 2.0 learning system
8. ⏳ Separate MCP server into own repo
9. ⏳ Enhance CI/CD with platform matrix

### Month 2:
10. ⏳ Create first automated improvement track
11. ⏳ Integrate upstream issue monitoring
12. ⏳ Add accessibility checks

---

## APPENDIX A: Command Reference for Implementation

### Merge Dependabot PRs:
```bash
# List all Dependabot PRs
gh pr list --author app/dependabot --state open

# Review and merge
gh pr checkout 12
npm install && npm test  # in mcp-server/
gh pr merge 12 --merge
```

### Create SECURITY.md:
```bash
# Use template from Section 1.2
cat > SECURITY.md << 'EOF'
[Template content]
EOF

git add SECURITY.md
git commit -m "docs: Add security policy with vulnerability reporting"
```

### Test Cross-Platform:
```bash
# Local testing
python -m pytest conductor-core/ -v --cov
cd mcp-server && npm test
cd ../conductor-vscode && npm test

# CI testing (after push)
# Check GitHub Actions for results
```

### Ralph Mode 2.0 Implementation:
```bash
# Create feature branch
git checkout -b feature/ralph-mode-2.0

# Create iteration logger
mkdir -p conductor-core/src/ralph
touch conductor-core/src/ralph/__init__.py
touch conductor-core/src/ralph/iteration_logger.py
touch conductor-core/src/ralph/pattern_analyzer.py
touch conductor-core/src/ralph/improvement_generator.py

# Implement components from Section 3.1
# ...

# Test with existing tracks
/conductor:implement --ralph --learning-enabled
```

---

**Document Status:** Draft  
**Next Review:** March 10, 2026  
**Stakeholders:** @edithatogo team, upstream maintainers, community

---

*This improvement plan integrates the Ralph Loop skill for autonomous self-improvement and learning, focusing on repo/skill design optimization, CI/CD enhancement, and strategic differentiation from upstream.*
