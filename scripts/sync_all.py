import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "conductor-core" / "src"))

from scripts.sync_skills import sync_skills
from scripts.validate_platforms import sync_platforms

def main():
    print("--- Phase 1: Synchronizing Global & Platform Skills ---")
    try:
        sync_skills()
        print("[OK] Skills synchronized successfully.")
    except Exception as e:
        print(f"[ERROR] Error synchronizing skills: {e}")
        return 1

    print("\n--- Phase 2: Synchronizing Repository-Local Platform Files ---")
    try:
        sync_platforms()
        print("[OK] Platform files synchronized successfully.")
    except Exception as e:
        print(f"[ERROR] Error synchronizing platform files: {e}")
        return 1

    print("\n[SUCCESS] Conductor Synchronization Complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())