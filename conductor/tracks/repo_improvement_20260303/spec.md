# Repository Improvement Track - March 2026

**Track ID:** `repo_improvement_20260303`  
**Created:** March 3, 2026  
**Status:** Ready for Implementation  
**Author:** AI Agent (via GitHub Research & Analysis)  
**Review Cycle:** Monthly  
**Priority:** P1-High  
**Duration:** 2-3 weeks

---

## Executive Summary

This track implements comprehensive repository improvements based on analysis of:
- ✅ **Our Fork PRs:** 0 open (clean slate)
- ✅ **Upstream Issues:** 11 open (2 P1 priority)
- ✅ **Upstream PRs:** 14 open (including our PR #93 with 83 commits)
- ✅ **SOTA Approaches:** Artifact inference, Ralph Mode, multi-VCS

**Key Objectives:**
1. Adopt upstream P1 improvements (artifact inference setup)
2. Implement Ralph Mode 2.0 with learning capabilities
3. Establish monthly improvement cycle automation
4. Address cross-platform compatibility issues
5. Prepare PR #93 for upstream merge

---

## Problem Statement

### Current State

**Our Fork (edithatogo/conductor-next):**
- ✅ Clean PR queue (0 open)
- ✅ All 13 tracks completed (~270 tasks)
- ⚠️ No automated improvement cycle
- ⚠️ Ralph Mode present but lacks learning capabilities
- ⚠️ Manual dependency management

**Upstream (gemini-cli-extensions/conductor):**
- 📊 11 open issues (2 P1 priority)
- 📊 14 open PRs (3 draft, 11 with reviews)
- 🎯 PR #137: Artifact inference setup (approved, ready to merge)
- 🎯 PR #124: Plan mode warning hook (approved, pending merge)
- 🎯 PR #86: Ralph Mode loop (draft, in development)
- 🎯 PR #93: **Our contribution** - Multi-VCS support (83 commits, 13 comments)

### Pain Points

1. **Manual Improvement Process:**
   - No scheduled improvement cycles
   - Reactive rather than proactive
   - Knowledge not captured systematically

2. **Ralph Mode Limitations:**
   - No iteration logging
   - No pattern recognition
   - No automated improvement generation
   - Cannot learn from past failures

3. **Upstream Lag:**
   - P1 improvements not adopted (#136, #122)
   - Risk of divergence from upstream
   - Missing community contributions

4. **Cross-Platform Issues:**
   - macOS `ls -I` incompatibility (PR #56)
   - Linux template finding bug (Issue #120)
   - Windows path issues (addressed in PR #93)

---

## Proposed Solution

### Phase 1: Immediate Actions (Days 1-3)

**1.1 Create Security Policy**
- Add SECURITY.md with vulnerability reporting
- Enable Dependabot security alerts
- Document security best practices

**1.2 Establish Improvement Infrastructure**
- Create improvement track template
- Define improvement workflow
- Set up automation scripts

**1.3 Upstream PR #93 Management**
- Engage with Google reviewers
- Address feedback within 24 hours
- Prevent merge conflicts via daily rebases

---

### Phase 2: Adopt Upstream P1 Improvements (Days 4-10)

**2.1 Artifact Inference Setup (from PR #137)**

**What:** Replace brittle `setup_state.json` with declarative artifact audit

**Key Features:**
- Priority Table mapping artifacts to setup sections
- Conductor-aware Greenfield/Brownfield detection
- Fast-forward logic for resume
- Self-healing for interrupted tracks
- Token efficiency (reduced prompt logic)

**Implementation Approach:**
```python
# State Priority Table (conceptual)
PRIORITY_TABLE = {
    'product.md': ['product_context', 'specification'],
    'tech-stack.md': ['technology_decisions'],
    'workflow.md': ['process_definition'],
    'tracks.md': ['track_registry'],
    'tracks/': ['implementation'],
}

# Maturity Detection
def detect_maturity(project_path):
    artifacts = scan_artifacts(project_path)
    
    # Ignore conductor/ directory and empty .git
    if not artifacts or artifacts == ['.git/']:
        return 'GREENFIELD'
    
    if 'product.md' in artifacts and 'workflow.md' in artifacts:
        return 'BROWNFIELD_COMPLETE'
    
    return 'BROWNFIELD_PARTIAL'
```

**Testing Strategy:**
- Test greenfield detection (empty project)
- Test brownfield detection (existing project)
- Test Conductor-aware detection (conductor/ dir present)
- Test resume from interrupted setup
- Measure token usage reduction (target: >20%)

---

**2.2 Plan Mode Warning Hook (from PR #124)**

**What:** Prevent conflicts with Gemini CLI's built-in plan mode

**Implementation:**
```javascript
// hooks/plan_mode_warning.js
const { registerHook } = require('@gemini-cli/hooks');

registerHook('BeforeToolCall', (toolCall) => {
  if (toolCall.name === 'PlanMode') {
    console.warn('⚠️  WARNING: Conductor manages planning lifecycle.');
    console.warn('Using built-in Plan Mode may cause state conflicts.');
    console.warn('Recommended: Use /conductor:newTrack and /conductor:implement instead.');
    
    // Optionally block or allow with warning
    return { action: 'WARN', message: 'Conductor conflict detected' };
  }
});
```

**Testing:**
- Trigger plan mode, verify warning appears
- Verify Conductor commands still work
- Test with warning disabled (user preference)

---

### Phase 3: Ralph Mode 2.0 Implementation (Days 11-17)

**3.1 Architecture Overview**

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

**3.2 Component 1: Iteration Logger**

**File:** `conductor-core/src/ralph/iteration_logger.py`

```python
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
    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or Path('.conductor/ralph-logs/')
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def log_iteration(self, iteration: RalphIteration):
        """Log iteration to JSONL file."""
        log_file = self.storage_path / f"{iteration.track_id}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(iteration.__dict__, default=str) + '\n')
    
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

**Tests:**
- Test logging to JSONL file
- Test retrieval by track ID
- Test with missing log file
- Test concurrent writes

---

**3.3 Component 2: Pattern Analyzer**

**File:** `conductor-core/src/ralph/pattern_analyzer.py`

```python
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
    
    def get_success_patterns(self) -> dict:
        """Find patterns in successful iterations."""
        successful = [
            i for log_file in self.logger.storage_path.glob('*.jsonl')
            for i in self.logger.get_track_history(log_file.stem)
            if i.status == 'SUCCESS'
        ]
        
        if not successful:
            return {}
        
        return {
            'avg_cycles_per_task': sum(i.cycle_number for i in successful) / len(successful),
            'avg_tests_per_task': sum(i.tests_written for i in successful) / len(successful),
            'common_error_types_resolved': Counter(
                i.error_type for i in successful if i.cycle_number > 1
            )
        }
```

**Tests:**
- Test recurring failure detection
- Test success pattern analysis
- Test with empty logs
- Test with mixed success/failure data

---

**3.4 Component 3: Improvement Generator**

**File:** `conductor-core/src/ralph/improvement_generator.py`

```python
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
        if success_patterns and success_patterns['avg_cycles_per_task'] > 3:
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
"""
        )
        return track
```

**Tests:**
- Test improvement generation from failures
- Test improvement generation from efficiency metrics
- Test track creation
- Test with no patterns

---

**3.5 Enhanced Ralph Mode Directive**

**File:** `hooks/ralph-mode/directive.md` (updated)

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
   d. Call 'ralph_end' with status='SUCCESS' + analysis summary

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

### Phase 4: Automation & CI/CD (Days 18-21)

**4.1 Monthly Improvement Automation**

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

**4.2 GitHub Action:** `.github/workflows/monthly-improvement.yml`

```yaml
name: Monthly Repository Improvement

on:
  schedule:
    # First Monday of every month at 09:00 UTC
    - cron: '0 9 1-7 * 1'
  workflow_dispatch:

jobs:
  improvement:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Start Improvement Cycle
        run: |
          ./scripts/start_improvement_cycle.sh
      
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: 'conductor: Create monthly improvement track'
          branch: improvement/$(date +%Y%m%d)
          title: 'Monthly Repository Improvement - $(date +%Y-%m)'
          body: 'Automated monthly improvement track created by CI/CD.'
```

---

## Success Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| PRs Merged | N/A | 100% Dependabot | Count / Total |
| Security Vulnerabilities | 0 critical | 0 critical | Security scan |
| Upstream Issues Adopted | 0 | ≥2 per cycle | Count |
| Ralph Mode Iterations | 0 logged | ≥10 per track | Iteration logs |
| Pattern Improvements | 0 | ≥1 per cycle | Improvement generator |
| Test Coverage | 100% core | Maintain | Coverage reports |
| CI Duration | <15 min | <15 min | GitHub Actions |

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| PR #93 merge conflicts | MEDIUM | HIGH | Daily rebases, frequent communication |
| Upstream adopts our features | MEDIUM | MEDIUM | Maintain differentiation via Ralph 2.0 |
| Ralph Mode learning overhead | LOW | LOW | Optional feature, disabled by default |
| Cross-platform bugs | MEDIUM | HIGH | Enhanced CI matrix testing |

---

## References

- Upstream Issue #136: Brittle JSON state
- Upstream PR #137: Artifact inference setup
- Upstream Issue #122: Plan mode conflicts
- Upstream PR #124: Warning hook
- Upstream PR #86: Ralph Mode loop
- Upstream PR #93: Our Multi-VCS contribution
- Upstream PR #56: macOS compatibility

---

**Track Status:** Ready for Implementation  
**Next Step:** Create plan.md with TDD tasks  
**Estimated Duration:** 2-3 weeks  
**Priority:** P1-High
