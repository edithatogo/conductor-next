# Artifact Inference Setup - Test Scenarios

**Track:** artifact_inference_setup_20260304  
**Status:** Ready for Testing  
**Priority:** P1-High  
**Date:** March 4, 2026

---

## Overview

This document defines 5 test scenarios to validate the Artifact Inference Setup implementation. Each scenario tests a different project state and verifies the correct resume behavior.

---

## Test Environment Setup

**Prerequisites:**
- Clean test directory for each scenario
- Conductor installed and configured
- Access to `/conductor:setup` command

**Test Command:**
```bash
# For each scenario, create a fresh test directory
mkdir test_scenario_X && cd test_scenario_X
/conductor:setup
```

---

## Test Scenario 1: Fresh Greenfield Project

**Objective:** Verify that a completely empty project starts at Section 2.0

**Setup:**
```bash
mkdir test_greenfield && cd test_greenfield
# Empty directory - no files
/conductor:setup
```

**Expected Behavior:**
1. ✅ No artifacts detected
2. ✅ Target Section: 2.0 (fresh start)
3. ✅ No resume announcement
4. ✅ Proceeds normally to Project Discovery (Section 2.0.1)

**Expected Output:**
```
Welcome to Conductor. I will guide you through the following steps...
1. Project Discovery: Analyzing current directory...
[No artifacts found - starting fresh setup]
```

**Pass Criteria:**
- Setup starts at Section 2.0
- No resume messages
- Asks about project type (Greenfield/Brownfield)

---

## Test Scenario 2: Partial Setup (product.md only)

**Objective:** Verify fast-forward to Section 2.2 when product.md exists

**Setup:**
```bash
mkdir test_partial_product && cd test_partial_product
mkdir -p conductor
echo "# My Product" > conductor/product.md
/conductor:setup
```

**Expected Behavior:**
1. ✅ Artifact detected: `conductor/product.md`
2. ✅ Target Section: 2.2 (Product Guidelines)
3. ✅ Announcement: "Resuming setup: Product Guide is complete. Next: create Product Guidelines."
4. ✅ Immediately jumps to Section 2.2

**Expected Output:**
```
[PROJECT AUDIT]
Detected artifacts: conductor/product.md

Resuming setup: Product Guide is complete. Next: create Product Guidelines.
[Fast-forward to Section 2.2]
```

**Pass Criteria:**
- Detects product.md
- Announces correct resume message
- Jumps directly to Section 2.2
- Does NOT ask about product.md again

---

## Test Scenario 3: Partial Setup (workflow.md)

**Objective:** Verify fast-forward to Section 2.6 when workflow.md exists

**Setup:**
```bash
mkdir test_partial_workflow && cd test_partial_workflow
mkdir -p conductor
echo "# Workflow" > conductor/workflow.md
/conductor:setup
```

**Expected Behavior:**
1. ✅ Artifacts detected: workflow.md (and implied product.md, guidelines, tech-stack)
2. ✅ Target Section: 2.6 (Index generation)
3. ✅ Announcement: "Resuming setup: Workflow is defined. Next: generate project index."
4. ✅ Immediately jumps to Section 2.6

**Expected Output:**
```
[PROJECT AUDIT]
Detected artifacts: conductor/workflow.md

Resuming setup: Workflow is defined. Next: generate project index.
[Fast-forward to Section 2.6]
```

**Pass Criteria:**
- Detects workflow.md
- Announces correct resume message
- Jumps directly to Section 2.6
- Does NOT ask about previous sections

---

## Test Scenario 4: Complete Setup (Already Initialized)

**Objective:** Verify HALT when complete track exists

**Setup:**
```bash
mkdir test_complete && cd test_complete
mkdir -p conductor/tracks/test_track
echo "# Spec" > conductor/tracks/test_track/spec.md
echo "# Plan" > conductor/tracks/test_track/plan.md
echo "{}" > conductor/tracks/test_track/metadata.json
echo "# Index" > conductor/tracks/test_track/index.md
/conductor:setup
```

**Expected Behavior:**
1. ✅ Complete track detected (all 4 files)
2. ✅ Target: HALT
3. ✅ Announcement: "The project is already initialized. Use `/conductor:newTrack` or `/conductor:implement`."
4. ✅ Setup process halts

**Expected Output:**
```
[PROJECT AUDIT]
Detected complete track: conductor/tracks/test_track/

The project is already initialized. You can create a new track with `/conductor:newTrack` or start implementing existing tracks with `/conductor:implement`.
[HALT]
```

**Pass Criteria:**
- Detects all 4 track files
- Announces already initialized message
- Halts setup process
- Does NOT proceed with setup

---

## Test Scenario 5: Incomplete Track Cleanup

**Objective:** Verify automatic cleanup of incomplete track folders

**Setup:**
```bash
mkdir test_cleanup && cd test_cleanup
mkdir -p conductor/tracks/incomplete_track
echo "partial content" > conductor/tracks/incomplete_track/partial.md
/conductor:setup
```

**Expected Behavior:**
1. ✅ Incomplete track folder detected
2. ✅ Announcement: "Detected incomplete track folder. Cleaning up..."
3. ✅ Deletes `conductor/tracks/` directory
4. ✅ Announcement: "Incomplete track folder removed. Proceeding with fresh track generation."
5. ✅ Proceeds with Section 3.0

**Expected Output:**
```
[TRACK CLEANUP PRE-REQUISITE]
Detected existing track folder. Cleaning up to ensure clean, consistent state.
Incomplete track folder removed. Proceeding with fresh track generation.
[Proceed to Section 3.0]
```

**Pass Criteria:**
- Detects incomplete track
- Announces cleanup
- Deletes tracks directory
- Proceeds with fresh generation
- Does NOT fail or error

---

## Test Results Template

| Scenario | Expected Section | Actual Section | Pass/Fail | Notes |
|----------|-----------------|----------------|-----------|-------|
| 1. Fresh Greenfield | 2.0 | | | |
| 2. Partial (product.md) | 2.2 | | | |
| 3. Partial (workflow.md) | 2.6 | | | |
| 4. Complete Setup | HALT | | | |
| 5. Incomplete Track Cleanup | 3.0 | | | |

---

## Execution Instructions

**For each scenario:**

1. **Setup:**
   ```bash
   rm -rf test_scenario_*
   mkdir test_scenario_X && cd test_scenario_X
   # Follow scenario-specific setup above
   ```

2. **Run:**
   ```bash
   /conductor:setup
   ```

3. **Observe:**
   - Record announcements
   - Note which section it jumps to
   - Verify behavior matches expected

4. **Document:**
   - Fill in Test Results Template
   - Note any deviations
   - Screenshot output if needed

5. **Cleanup:**
   ```bash
   cd .. && rm -rf test_scenario_X
   ```

---

## Success Criteria

**All scenarios must pass:**
- ✅ Scenario 1: Starts at 2.0 (no artifacts)
- ✅ Scenario 2: Jumps to 2.2 (product.md detected)
- ✅ Scenario 3: Jumps to 2.6 (workflow.md detected)
- ✅ Scenario 4: HALTs (complete track detected)
- ✅ Scenario 5: Cleanup works (incomplete track removed)

**If any scenario fails:**
1. Document the failure
2. Identify root cause
3. Fix implementation
4. Re-run failed scenario

---

**Ready for Testing:** March 4, 2026  
**Test Lead:** [Assignee]  
**Estimated Duration:** 1-2 hours for all 5 scenarios
