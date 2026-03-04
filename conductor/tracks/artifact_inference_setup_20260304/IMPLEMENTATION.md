# Artifact Inference Setup - Implementation Track

**Track ID:** artifact_inference_setup_20260304  
**Created:** March 4, 2026  
**Priority:** P1-High  
**Estimated Duration:** 4-6 hours  
**Status:** Ready for Implementation

---

## Objective

Replace brittle `setup_state.json` with robust filesystem artifact audit approach from upstream PR #137.

---

## Implementation Plan

### Phase 1: Analysis (Complete)
- [x] Read ARTIFACT_INFERENCE_PLAN.md
- [x] Understand State Priority Table
- [x] Identify files to modify

### Phase 2: Implementation

#### Task 2.1: Modify setup.toml Section 1.1
**File:** `commands/conductor/setup.toml`  
**Change:** Replace old resume protocol with Artifact Audit Protocol

**Old (Section 1.1):**
```toml
## 1.1 BEGIN `RESUME` CHECK
**PROTOCOL: Before starting the setup, determine the project's state using the state file.**

1.  **Read State File:** Check for `conductor/setup_state.json`.
...
```

**New (Section 1.1):**
```toml
## 1.1 PROJECT AUDIT
**PROTOCOL: Before starting the setup, determine the project's state by auditing existing artifacts.**

1.  **Audit Artifacts:** Check the file system for:
    - `conductor/product.md`
    - `conductor/product-guidelines.md`
    - `conductor/tech-stack.md`
    - `conductor/code_styleguides/`
    - `conductor/workflow.md`
    - `conductor/index.md`
    - `conductor/tracks/<track_id>/` (check for all 4 files)

2.  **Determine Target Section:** Map using the State Priority Table (highest match wins).
    **DO NOT JUMP YET.**

3.  **Proceed to Section 2.0:** MUST establish Greenfield/Brownfield context before jumping.
```

#### Task 2.2: Add State Priority Table
**Location:** Section 1.1 of setup.toml  
**Add:** Complete State Priority Table mapping artifacts to sections

#### Task 2.3: Add Fast-Forward Resume Logic
**New Section 1.2:**
```toml
## 1.2 FAST-FORWARD RESUME CHECK
**PROTOCOL: After establishing project maturity, fast-forward to the appropriate section.**

1.  **Resume Fast-Forward Check:**
    -   If **Target Section** (from Section 1.1) is anything other than "Section 2.0":
        -   Announce the project maturity state (Greenfield/Brownfield) with specific reason
        -   **IMMEDIATELY JUMP** to the Target Section
    -   If Target Section is "Section 2.0", proceed normally to Section 2.0
```

#### Task 2.4: Remove State File Writes
**Remove from these sections:**
- Section 2.1: Remove state write after product.md creation
- Section 2.2: Remove state write after product-guidelines.md
- Section 2.3: Remove state write after tech-stack.md
- Section 2.4: Remove state write after code_styleguides/
- Section 2.5: Remove state write after workflow.md
- Section 3.3: Remove state write after track generation

**Search for:** `setup_state.json` and remove all references

#### Task 2.5: Add Track Cleanup
**Section 3.0 Pre-Requisite:**
```toml
**Pre-Requisite (Cleanup):** If resuming Section 3.0 and `conductor/tracks/` exists but is incomplete:
1. Announce: "Detected incomplete track folder. Cleaning up to ensure clean, consistent state."
2. Delete the entire `conductor/tracks/` directory
3. Proceed with Section 3.0
```

### Phase 3: Testing

#### Test Scenarios:
1. **Fresh Greenfield** - No artifacts, starts at Section 2.0
2. **Partial Setup (product.md only)** - Jumps to Section 2.2
3. **Partial Setup (workflow.md)** - Jumps to Section 2.6
4. **Complete Setup** - HALTs with "already initialized" message
5. **Incomplete Track Cleanup** - Deletes incomplete track, restarts Section 3.0

---

## Success Criteria

- [ ] All state file references removed
- [ ] Artifact audit protocol implemented
- [ ] State Priority Table working
- [ ] Fast-forward resume working
- [ ] Track cleanup working
- [ ] All 5 test scenarios pass
- [ ] No breaking changes for existing users

---

## References

- **Upstream PR #137:** https://github.com/gemini-cli-extensions/conductor/pull/137
- **Upstream Issue #136:** https://github.com/gemini-cli-extensions/conductor/issues/136
- **Implementation Guide:** `conductor/archive/repo_improvement_20260303/ARTIFACT_INFERENCE_PLAN.md`

---

**Next Step:** Begin Task 2.1 - Modify setup.toml Section 1.1
