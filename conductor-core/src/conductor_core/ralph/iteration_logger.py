from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


class RalphIteration(BaseModel):
    """Details of a single Ralph loop iteration."""

    track_id: str
    task_id: str
    iteration: int
    status: str  # SUCCESS, FAILURE, STUCK
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    files_changed: list[str] = []
    tests_run: int = 0
    tests_failed: int = 0
    metadata: dict[str, Any] = {}

    def complete(self, status: str, error: Optional[str] = None, files: list[str] = None):
        """Finalize iteration data."""
        self.status = status
        self.error_message = error
        self.files_changed = files or []
        self.end_time = datetime.now(timezone.utc)
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()


class IterationLogger:
    """Logs Ralph iterations for pattern analysis and learning."""

    def __init__(self, log_dir: str | Path = ".conductor/ralph-logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_iteration(self, iteration: RalphIteration):
        """Save iteration data to a JSON file."""
        # Create a unique filename for this iteration
        timestamp = iteration.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"{iteration.track_id}_{iteration.task_id}_{timestamp}_{iteration.iteration}.json"
        
        file_path = self.log_dir / filename
        with file_path.open("w", encoding="utf-8") as f:
            f.write(iteration.model_dump_json(indent=2))

    def get_history(self, track_id: Optional[str] = None) -> list[RalphIteration]:
        """Retrieve historical iteration logs."""
        iterations = []
        for file_path in self.log_dir.glob("*.json"):
            try:
                data = json.loads(file_path.read_text(encoding="utf-8"))
                iter_obj = RalphIteration(**data)
                if track_id is None or iter_obj.track_id == track_id:
                    iterations.append(iter_obj)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Warning: Failed to load log {file_path}: {e}")
                
        return sorted(iterations, key=lambda x: x.start_time)
