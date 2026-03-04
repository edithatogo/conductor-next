# Script Encoding Fix Task

**Issue:** Emoji characters cause UnicodeEncodeError on Windows (cp1252 encoding)

**Affected Files:**
- scripts/collect_improvement_data.py
- scripts/security_scan.py
- scripts/create_improvement_track.py
- scripts/start_improvement_cycle.sh

**Solution:** Replace all emoji with ASCII-compatible text

**Priority:** P1-High (blocks automation testing)

---

## Fix Required

Replace in all scripts:
- 🚀 → [READY] or just remove
- 🔒 → [SECURITY] or just remove
- 📋 → [TASK] or just remove
- ✅ → [OK] or just remove
- ❌ → [ERROR] or just remove
- ⏭️ → [SKIP] or just remove
- 📊 → [SUMMARY] or just remove

---

## Implementation

**Option 1:** Remove all emojis (simplest)
**Option 2:** Replace with ASCII text labels
**Option 3:** Add UTF-8 encoding declaration at script start

**Recommended:** Option 1 for clean output

---

**Status:** Ready to implement
**Estimated Time:** 30 minutes
**Impact:** Enables cross-platform compatibility
