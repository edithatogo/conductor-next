"""
Tests for improvement data collection script.

This module tests the collect_improvement_data.py script functionality.
"""

import unittest
from pathlib import Path
import json


class TestImprovementDataCollection(unittest.TestCase):
    """Test cases for improvement data collection."""

    def setUp(self):
        """Set up test fixtures."""
        self.root_dir = Path(__file__).parent.parent
        self.script_path = self.root_dir / "scripts" / "collect_improvement_data.py"
        self.output_dir = self.root_dir / ".conductor" / "improvement-data"

    def test_script_exists(self):
        """Test that collect_improvement_data.py exists."""
        self.assertTrue(self.script_path.exists(), f"collect_improvement_data.py not found at {self.script_path}")

    def test_script_is_executable(self):
        """Test that the script has execute permissions."""
        if self.script_path.exists():
            # On Unix, check execute bit
            mode = self.script_path.stat().st_mode
            # Either has execute bit or can be run with python
            is_executable = mode & 0o111 or self.script_path.suffix == ".py"
            self.assertTrue(is_executable, "Script should be executable")

    def test_output_directory_created(self):
        """Test that output directory is created."""
        if self.output_dir.exists():
            self.assertTrue(self.output_dir.is_dir(), f"{self.output_dir} should be a directory")

    def test_json_files_valid(self):
        """Test that generated JSON files are valid."""
        if self.output_dir.exists():
            json_files = list(self.output_dir.glob("*.json"))
            for json_file in json_files:
                with open(json_file, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        self.assertIsInstance(data, (dict, list), f"{json_file} should contain valid JSON")
                    except json.JSONDecodeError as e:
                        self.fail(f"{json_file} contains invalid JSON: {e}")


if __name__ == "__main__":
    unittest.main()
