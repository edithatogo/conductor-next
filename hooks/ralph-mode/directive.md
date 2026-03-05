## 🔴 RALPH MODE 2.0: AUTONOMOUS SELF-IMPROVEMENT
**ATTENTION:** Announce verbatim
    > 🔁 Operating in **RALPH MODE 2.0** with learning enabled.

**INSTRUCTIONS:**
1.  **Initialization:** Ensure the **Ralph Loop State** is excluded from version control.
2.  **Execute Standard Protocol:** Follow the "TRACK IMPLEMENTATION" protocol (Phase 3 of the plan).
3.  **AUTONOMOUS CYCLE:**
    -   For each task, execute this **RALPH CYCLE**:
        1.  **RED:** Write failing tests based on the **Specification**.
        2.  **GREEN:** Implement code to pass tests.
        3.  **VERIFY:** Run tests.
        4.  **LOG:** After each attempt (Pass or Fail), log the iteration:
            ```bash
            python scripts/ralph_cli.py log --track-id {{TRACK_ID}} --task-id {{TASK_ID}} --iteration {{N}} --status {{SUCCESS|FAILURE}} [--error "{{ERROR}}"]
            ```
        5.  **ANALYZE (IF STUCK):** If you fail more than 3 times on the same task, run:
            ```bash
            python scripts/ralph_cli.py analyze --track-id {{TRACK_ID}}
            ```
            Incorporate Ralph's suggestions into your next plan.
        6.  **RECORD:** Update plan status to [x] and commit changes.
4.  **SKIP MANUAL TASKS:** Mark any task involving "Manual Verification" as [x] immediately. Ralph's tests are the only source of truth.
5.  **COMPLETION:**
    -   **WHEN DONE:** Call 'ralph_end' with status='SUCCESS' and message='Task complete: {{COMPLETION_WORD}}'.
    -   **IF STUCK:** If you are unable to proceed due to ambiguity or tool failures, call 'ralph_end' with status='STUCK' and explain why.
