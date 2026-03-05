from __future__ import annotations

from typing import Any, Optional

from .iteration_logger import IterationLogger, RalphIteration


class PatternAnalyzer:
    """Analyzes Ralph iteration logs to identify recurring issues."""

    def __init__(self, logger: Optional[IterationLogger] = None):
        self.logger = logger or IterationLogger()

    def analyze_failures(self, track_id: Optional[str] = None) -> list[dict[str, Any]]:
        """Identify common failure patterns."""
        history = self.logger.get_history(track_id)
        failures = [i for i in history if i.status in ("FAILURE", "STUCK")]
        
        if not failures:
            return []
            
        patterns = {}
        for f in failures:
            # Group by error message (first line)
            error_line = (f.error_message or "Unknown Error").split("\n")[0]
            if error_line not in patterns:
                patterns[error_line] = {
                    "count": 0,
                    "tasks": set(),
                    "files": set(),
                }
            patterns[error_line]["count"] += 1
            patterns[error_line]["tasks"].add(f.task_id)
            if f.files_changed:
                patterns[error_line]["files"].update(f.files_changed)
                
        # Format for reporting
        report = []
        for error, data in patterns.items():
            report.append({
                "error": error,
                "frequency": data["count"],
                "affected_tasks": list(data["tasks"]),
                "affected_files": list(data["files"]),
                "impact": "HIGH" if data["count"] > 3 else "MEDIUM"
            })
            
        return sorted(report, key=lambda x: x["frequency"], reverse=True)

    def suggest_improvements(self, track_id: Optional[str] = None) -> list[str]:
        """Generate human-readable improvement suggestions."""
        patterns = self.analyze_failures(track_id)
        suggestions = []
        
        for p in patterns:
            if p["frequency"] >= 2:
                suggestions.append(
                    f"Frequent failure detected: '{p['error']}' ({p['frequency']} times). "
                    f"Check logic in: {', '.join(p['affected_files'][:3])}"
                )
                
        return suggestions
