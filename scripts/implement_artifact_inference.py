#!/usr/bin/env python3
"""
Implement Artifact Inference Setup in setup.toml
Replaces state-file-based resume with artifact audit approach.
"""

from pathlib import Path

# New Section 1.1 content
NEW_SECTION_1_1 = """## 1.1 PROJECT AUDIT
**PROTOCOL: Before starting the setup, determine the project's state by auditing existing artifacts.**

1.  **Audit Artifacts:** Check the file system for the following artifacts (in priority order):
    -   Complete track: `conductor/tracks/<track_id>/` containing ALL of: `spec.md`, `plan.md`, `metadata.json`, `index.md`
    -   `conductor/index.md` (top-level)
    -   `conductor/workflow.md`
    -   `conductor/code_styleguides/` directory
    -   `conductor/tech-stack.md`
    -   `conductor/product-guidelines.md`
    -   `conductor/product.md`

2.  **Determine Target Section:** Map using the **State Priority Table** (highest match wins):

    | **Artifact Exists** | **Target Section** | **Announcement** |
    | :--- | :--- | :--- |
    | Complete track (all 4 files) | **HALT** | "The project is already initialized. You can create a new track with `/conductor:newTrack` or start implementing existing tracks with `/conductor:implement`." |
    | `conductor/index.md` | **Section 3.0** | "Resuming setup: Scaffolding is complete. Next: generate the first track. (Note: If an incomplete track folder was detected, we will restart this step to ensure a clean, consistent state)." |
    | `conductor/workflow.md` | **Section 2.6** | "Resuming setup: Workflow is defined. Next: generate project index." |
    | `conductor/code_styleguides/` | **Section 2.5** | "Resuming setup: Guides/Tech Stack configured. Next: define project workflow." |
    | `conductor/tech-stack.md` | **Section 2.4** | "Resuming setup: Tech Stack defined. Next: select Code Styleguides." |
    | `conductor/product-guidelines.md` | **Section 2.3** | "Resuming setup: Guidelines are complete. Next: define the Technology Stack." |
    | `conductor/product.md` | **Section 2.2** | "Resuming setup: Product Guide is complete. Next: create Product Guidelines." |
    | (None) | **Section 2.0** | (None) |

3.  **Proceed to Section 2.0:** MUST establish Greenfield/Brownfield context before jumping to the target section.

---

## 1.2 FAST-FORWARD RESUME CHECK
**PROTOCOL: After establishing project maturity, fast-forward to the appropriate section.**

1.  **Resume Fast-Forward Check:**
    -   If **Target Section** (from Section 1.1) is anything other than "Section 2.0":
        -   Announce the project maturity state (Greenfield/Brownfield) with specific reason
        -   **IMMEDIATELY JUMP** to the Target Section
    -   If Target Section is "Section 2.0", proceed normally to Section 2.0

---

## 1.3 PRE-INITIALIZATION OVERVIEW"""

def main():
    setup_file = Path('commands/conductor/setup.toml')
    
    print(f"Reading {setup_file}...")
    content = setup_file.read_text(encoding='utf-8')
    
    # Find and replace Section 1.1
    old_start = "## 1.1 BEGIN `RESUME` CHECK"
    old_end = "## 1.2 PRE-INITIALIZATION OVERVIEW"
    
    start_idx = content.find(old_start)
    end_idx = content.find(old_end)
    
    if start_idx == -1 or end_idx == -1:
        print("❌ Could not find Section 1.1")
        return
    
    # Replace Section 1.1
    new_content = content[:start_idx] + NEW_SECTION_1_1 + content[end_idx:]
    
    # Write back
    setup_file.write_text(new_content, encoding='utf-8')
    print(f"✅ Updated {setup_file}")
    print("✅ Artifact Inference Setup implemented!")
    print("\nNext: Remove setup_state.json references from other sections")

if __name__ == '__main__':
    main()
