#!/usr/bin/env python3
"""
Add track cleanup pre-requisite to Section 3.0 in setup.toml
"""

from pathlib import Path

# Track cleanup pre-requisite content
TRACK_CLEANUP = """
### 3.0.1 Pre-Requisite (Track Cleanup)
**PROTOCOL: Before generating the first track, ensure clean state by removing incomplete track folders.**

1.  **Check for Incomplete Tracks:** Check if `conductor/tracks/` directory exists.
2.  **If Exists:**
    -   Announce: "Detected existing track folder. Cleaning up to ensure clean, consistent state."
    -   **Delete:** Remove the entire `conductor/tracks/` directory
    -   **Confirm:** Announce: "Incomplete track folder removed. Proceeding with fresh track generation."
3.  **Continue:** Immediately proceed to Section 3.1.
"""

def main():
    setup_file = Path('commands/conductor/setup.toml')
    
    print(f"Reading {setup_file}...")
    content = setup_file.read_text(encoding='utf-8')
    
    # Find Section 3.0 header (both occurrences)
    section_header = "## 3.0 INITIAL PLAN AND TRACK GENERATION"
    section_subheader = "**PROTOCOL: Interactively define project requirements"
    
    # Replace in both locations
    old_pattern = f"{section_header}\n{section_subheader}"
    new_pattern = f"{section_header}\n{section_subheader}{TRACK_CLEANUP}"
    
    # Replace all occurrences
    new_content = content.replace(old_pattern, new_pattern)
    
    if new_content != content:
        setup_file.write_text(new_content, encoding='utf-8')
        print(f"✅ Added track cleanup pre-requisite to {setup_file}")
        print("✅ Track cleanup pre-requisite COMPLETE!")
    else:
        print("⚠️  No changes made")

if __name__ == '__main__':
    main()
