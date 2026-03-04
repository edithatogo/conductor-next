#!/usr/bin/env python3
"""
Remove all setup_state.json references from setup.toml
Completes Artifact Inference Setup implementation.
"""

from pathlib import Path
import re

def main():
    setup_file = Path('commands/conductor/setup.toml')
    
    print(f"Reading {setup_file}...")
    content = setup_file.read_text(encoding='utf-8')
    original = content
    
    # Pattern 1: Remove "Initialize State File" steps
    pattern1 = r'\s*-\s*\*\*Initialize State File:\*\*.*?content:\s*`setup_state\.json`.*?\n'
    content = re.sub(pattern1, '', content, flags=re.DOTALL)
    
    # Pattern 2: Remove "Commit State" steps
    pattern2 = r'\s*-\s*\*\*Commit State:\*\*.*?`conductor/setup_state\.json`.*?\n'
    content = re.sub(pattern2, '', content, flags=re.DOTALL)
    
    # Pattern 3: Remove standalone Commit State paragraphs
    pattern3 = r'\s*\*\*Commit State:\*\*.*?`conductor/setup_state\.json`.*?\n'
    content = re.sub(pattern3, '', content, flags=re.DOTALL)
    
    # Pattern 4: Remove Read State File steps
    pattern4 = r'\s*\*\*Read State File:\*\*.*?`conductor/setup_state\.json`.*?\n'
    content = re.sub(pattern4, '', content, flags=re.DOTALL)
    
    # Pattern 5: Remove specific setup_state.json references
    content = content.replace('`conductor/setup_state.json`', '')
    content = content.replace('`setup_state.json`', '')
    
    # Pattern 6: Remove state initialization content lines
    pattern6 = r'\s*`{"last_successful_step":\s*"[^"]*"}`'
    content = re.sub(pattern6, '', content)
    
    if content != original:
        setup_file.write_text(content, encoding='utf-8')
        print(f"✅ Removed setup_state.json references from {setup_file}")
        
        # Count removals
        removals = original.count('setup_state') - content.count('setup_state')
        print(f"✅ Removed {removals} setup_state.json references")
        print("✅ Artifact Inference Setup COMPLETE!")
    else:
        print("⚠️  No changes made")

if __name__ == '__main__':
    main()
