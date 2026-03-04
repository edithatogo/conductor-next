#!/usr/bin/env python3
"""
Fix emoji encoding in automation scripts for Windows compatibility.
Replaces emoji with ASCII-compatible text.
"""

import re
from pathlib import Path

# Emoji replacements
REPLACEMENTS = {
    '🚀': '[READY]',
    '🔒': '[SECURITY]',
    '📋': '[TASK]',
    '✅': '[OK]',
    '❌': '[ERROR]',
    '⏭️': '[SKIP]',
    '📊': '[SUMMARY]',
    '🔍': '[CHECK]',
    '🎯': '[TARGET]',
    '⚠️': '[WARNING]',
    '💡': '[TIP]',
    '📁': '[FOLDER]',
    '📝': '[NOTE]',
    '📌': '[PIN]',
    '🔄': '[RETRY]',
    '⏳': '[WAIT]',
    '🎉': '[SUCCESS]',
}

def fix_file(filepath: Path):
    """Replace all emoji in a file with ASCII text."""
    print(f"Fixing: {filepath}")
    
    content = filepath.read_text(encoding='utf-8')
    original = content
    
    for emoji, replacement in REPLACEMENTS.items():
        content = content.replace(emoji, replacement)
    
    if content != original:
        filepath.write_text(content, encoding='utf-8')
        print(f"  ✓ Fixed {filepath.name}")
    else:
        print(f"  - No changes needed")

def main():
    """Fix all automation scripts."""
    scripts_dir = Path(__file__).parent.parent / 'scripts'
    
    # Fix Python scripts
    for script in scripts_dir.glob('*.py'):
        if 'emoji' not in script.name.lower():
            fix_file(script)
    
    print("\n✅ All scripts fixed for Windows compatibility!")
    print("\nNext: Test scripts with: python scripts/collect_improvement_data.py")

if __name__ == '__main__':
    main()
