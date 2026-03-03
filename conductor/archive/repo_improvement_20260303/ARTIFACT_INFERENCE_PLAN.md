# Artifact Inference Setup Implementation Plan

**Track:** repo_improvement_20260303  
**Task:** 2.1 - Adopt Artifact Inference Setup (from upstream PR #137)  
**Status:** Analysis Complete - Ready for Implementation  
**Priority:** P1-High  
**Date:** March 3, 2026

---

## Executive Summary

This document outlines the implementation plan for adopting the **Artifact Inference Setup** approach from upstream PR #137. This replaces the brittle `setup_state.json` file-based state management with a robust filesystem artifact audit approach.

**Key Benefits:**
- ✅ **Deterministic state mapping** - Files either exist or don't (no corruption risk)
- ✅ **Transparent state** - Users can see progress by looking at files
- ✅ **Self-healing** - Automatically cleans up incomplete tracks
- ✅ **Token efficient** - No redundant state file writes
- ✅ **Seamless resume** - Fast-forward to correct section based on artifacts

---

## Current State (Before)

**State Management:**
```json
{
  "last_successful_step": "2.3_tech_stack"
}
```

**Problems:**
1. If JSON file deleted → setup process breaks
2. If out of sync → forces manual patching or restart
3. Frequent file I/O wastes tokens
4. Hidden state (user can't see progress)
5. Fragile (corrupted JSON breaks everything)

---

## Target State (After)

**State Inference:**
```
Artifacts Found → Target Section
product.md → Section 2.2
product-guidelines.md → Section 2.3
tech-stack.md → Section 2.4
code_styleguides/ → Section 2.5
workflow.md → Section 2.6
index.md → Section 3.0
Complete track → HALT (already initialized)
```

**Benefits:**
1. No state file to corrupt
2. Visible progress (files in conductor/)
3. Automatic cleanup of incomplete tracks
4. Token efficient (no state writes)
5. Resilient (files either exist or don't)

---

## State Priority Table

| **Artifact Exists** | **Target Section** | **Announcement** |
| :--- | :--- | :--- |
| Complete track (`spec.md`, `plan.md`, `metadata.json`, `index.md`) | **HALT** | "The project is already initialized. Use `/conductor:newTrack` or `/conductor:implement`." |
| `conductor/index.md` | **Section 3.0** | "Resuming setup: Scaffolding is complete. Next: generate the first track." |
| `conductor/workflow.md` | **Section 2.6** | "Resuming setup: Workflow is defined. Next: generate project index." |
| `conductor/code_styleguides/` | **Section 2.5** | "Resuming setup: Guides/Tech Stack configured. Next: define project workflow." |
| `conductor/tech-stack.md` | **Section 2.4** | "Resuming setup: Tech Stack defined. Next: select Code Styleguides." |
| `conductor/product-guidelines.md` | **Section 2.3** | "Resuming setup: Guidelines are complete. Next: define the Technology Stack." |
| `conductor/product.md` | **Section 2.2** | "Resuming setup: Product Guide is complete. Next: create Product Guidelines." |
| (None) | **Section 2.0** | (None - fresh start) |

**Priority Rule:** Highest match wins (evaluated top-to-bottom)

---

## Implementation Mapping

### Artifact → Section Flow

```
Section 2.0  ← (No artifacts - Fresh start)
    ↓
Section 2.1  ← product.md exists
    ↓
Section 2.2  ← product-guidelines.md exists
    ↓
Section 2.3  ← tech-stack.md exists
    ↓
Section 2.4  ← code_styleguides/ exists
    ↓
Section 2.5  ← workflow.md exists
    ↓
Section 2.6  ← index.md exists
    ↓
Section 3.0  ← Complete track (HALT)
```

---

## Required Changes

### 1. Remove State File References

**Files to modify:**
- `commands/conductor/setup.toml`

**Changes:**
- Remove all references to `setup_state.json`
- Remove state file write operations after each section
- Remove old resume protocol (Section 1.1)

**Specific locations:**
- Section 1.1: Replace with Artifact Audit Protocol
- Section 2.1: Remove state write after product.md creation
- Section 2.2: Remove state write after product-guidelines.md
- Section 2.3: Remove state write after tech-stack.md
- Section 2.4: Remove state write after code_styleguides/
- Section 2.5: Remove state write after workflow.md
- Section 3.3: Remove state write after track generation

---

### 2. Add Artifact Audit Protocol

**New Section 1.1:**
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

---

### 3. Add Fast-Forward Resume Logic

**New Section 1.3:**
```toml
## 1.3 FAST-FORWARD RESUME CHECK
**PROTOCOL: After establishing project maturity, fast-forward to the appropriate section.**

1.  **Resume Fast-Forward Check:**
    -   If **Target Section** (from Section 1.1) is anything other than "Section 2.0":
        -   Announce the project maturity state (Greenfield/Brownfield) with specific reason
        -   **IMMEDIATELY JUMP** to the Target Section
    -   If Target Section is "Section 2.0", proceed normally to Section 2.0
```

---

### 4. Add Track Directory Cleanup

**Section 3.0 Pre-Requisite:**
```toml
**Pre-Requisite (Cleanup):** If resuming Section 3.0 and `conductor/tracks/` exists but is incomplete:
1.  Announce: "Detected incomplete track folder. Cleaning up to ensure clean, consistent state."
2.  Delete the entire `conductor/tracks/` directory
3.  Proceed with Section 3.0
```

---

### 5. Enhance Brownfield Detection

**Update Section 2.0.1:**
```toml
- **Brownfield Indicators:**
  - Check for `.git`, `.svn`, `.hg` directories
  - Execute `git status --porcelain` (ignore `conductor/` directory changes)
  - Check for: `package.json`, `pom.xml`, `requirements.txt`, `go.mod`, `Cargo.toml`
  - Check source directories: `src/`, `app/`, `lib/`, `bin/`

- **User Announcement:** State the SPECIFIC indicator found
  (e.g., "because I found a `package.json` file")
```

---

## Implementation Steps

### Step 1: Backup Current State
```bash
# Backup current setup.toml
cp commands/conductor/setup.toml commands/conductor/setup.toml.backup
```

### Step 2: Modify setup.toml
1. Replace Section 1.1 with Artifact Audit Protocol
2. Add Section 1.3 (Fast-Forward Resume)
3. Remove all state file write operations
4. Add track cleanup pre-requisite in Section 3.0
5. Enhance brownfield detection in Section 2.0.1

### Step 3: Test Scenarios

**Test 1: Fresh Greenfield**
```bash
mkdir test-greenfield && cd test-greenfield
/conductor:setup
# Expected: Starts at Section 2.0, no artifacts found
```

**Test 2: Partial Setup (product.md only)**
```bash
mkdir test-partial && cd test-partial
mkdir -p conductor
echo "# Product" > conductor/product.md
/conductor:setup
# Expected: Announces "Product Guide complete", jumps to Section 2.2
```

**Test 3: Complete Setup**
```bash
mkdir test-complete && cd test-complete
# Full conductor/ directory with all artifacts
/conductor:setup
# Expected: Announces "already initialized", HALTs
```

**Test 4: Incomplete Track Cleanup**
```bash
mkdir test-cleanup && cd test-cleanup
mkdir -p conductor/tracks/incomplete_track
echo "partial" > conductor/tracks/incomplete_track/partial.md
/conductor:setup
# Expected: Deletes incomplete_track, restarts Section 3.0
```

### Step 4: Update Documentation
- Update `conductor/improvement_workflow.md` to reflect new approach
- Update `templates/improvement_track_template.md`
- Remove references to `setup_state.json` from all docs

### Step 5: Remove setup_state.json from .gitignore
```bash
# Check if setup_state.json is in .gitignore
grep setup_state.json .gitignore
# Remove if present
```

---

## Testing Checklist

- [ ] Fresh greenfield project starts at Section 2.0
- [ ] product.md exists → jumps to Section 2.2
- [ ] product-guidelines.md exists → jumps to Section 2.3
- [ ] tech-stack.md exists → jumps to Section 2.4
- [ ] code_styleguides/ exists → jumps to Section 2.5
- [ ] workflow.md exists → jumps to Section 2.6
- [ ] index.md exists → jumps to Section 3.0
- [ ] Complete track → HALTs with message
- [ ] Incomplete track → Cleaned up and restarts Section 3.0
- [ ] Brownfield detection announces specific indicator
- [ ] No state file writes occur
- [ ] Resume works after interruption at any section

---

## Migration Path

**For Existing Users:**
1. If `setup_state.json` exists, read it once
2. Map to corresponding artifact:
   - `2.1_product_guide` → Check for `product.md`
   - `2.2_product_guidelines` → Check for `product-guidelines.md`
   - `2.3_tech_stack` → Check for `tech-stack.md`
   - `2.4_code_styleguides` → Check for `code_styleguides/`
   - `2.5_workflow` → Check for `workflow.md`
   - `3.3_initial_track_generated` → Check for complete track
3. Delete `setup_state.json` after migration
4. Announce: "Migrated to artifact-based state management"

---

## Success Metrics

- [ ] All 5 test scenarios pass
- [ ] No state file writes in code
- [ ] Artifact audit works correctly
- [ ] Fast-forward resume works for all sections
- [ ] Incomplete track cleanup works
- [ ] Brownfield detection enhanced
- [ ] Documentation updated
- [ ] No breaking changes for users

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking existing setups | Low | High | Migration path provided |
| Artifact detection bugs | Medium | Medium | Comprehensive testing |
| User confusion (no state file) | Low | Low | Clear announcements |
| Incomplete track false positive | Low | Medium | Strict file requirements |

---

## References

- **Upstream PR #137:** https://github.com/gemini-cli-extensions/conductor/pull/137
- **Upstream Issue #136:** https://github.com/gemini-cli-extensions/conductor/issues/136
- **Implementation Approach:** Declarative "Artifact Audit" replacing imperative state management

---

**Next Step:** Implement changes to `commands/conductor/setup.toml` following this plan.

**Estimated Effort:** M (4-6 hours)  
**Priority:** P1-High (addresses upstream P1 issue)
