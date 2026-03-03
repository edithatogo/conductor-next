"""
Tests for monthly improvement GitHub Action workflow.

This module tests the presence and validity of the monthly-improvement.yml workflow file.
"""

import unittest
from pathlib import Path
import yaml


class TestMonthlyImprovementWorkflow(unittest.TestCase):
    """Test cases for monthly improvement workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.root_dir = Path(__file__).parent.parent
        self.workflow_file = self.root_dir / ".github" / "workflows" / "monthly-improvement.yml"
        self.workflow_content = None
        
        if self.workflow_file.exists():
            self.workflow_content = self.workflow_file.read_text(encoding='utf-8')

    def test_workflow_file_exists(self):
        """Test that monthly-improvement.yml exists."""
        self.assertTrue(
            self.workflow_file.exists(),
            f"monthly-improvement.yml not found at {self.workflow_file}"
        )

    def test_workflow_file_not_empty(self):
        """Test that workflow file is not empty."""
        self.assertIsNotNone(
            self.workflow_content,
            "Workflow file is empty"
        )
        self.assertGreater(
            len(self.workflow_content),
            100,
            "Workflow file is too short (< 100 characters)"
        )

    def test_workflow_yaml_valid(self):
        """Test that workflow YAML is valid."""
        self.assertIsNotNone(self.workflow_content)
        try:
            data = yaml.safe_load(self.workflow_content)
            self.assertIsInstance(data, dict)
        except yaml.YAMLError as e:
            self.fail(f"Workflow YAML is invalid: {e}")

    def test_workflow_has_schedule_trigger(self):
        """Test that workflow has schedule trigger."""
        self.assertIsNotNone(self.workflow_content)
        # Check for cron schedule
        self.assertIn(
            "schedule:",
            self.workflow_content,
            "Workflow missing schedule trigger"
        )
        self.assertIn(
            "cron:",
            self.workflow_content,
            "Workflow missing cron expression"
        )

    def test_workflow_has_workflow_dispatch(self):
        """Test that workflow has manual trigger."""
        self.assertIsNotNone(self.workflow_content)
        self.assertIn(
            "workflow_dispatch:",
            self.workflow_content,
            "Workflow missing workflow_dispatch trigger"
        )

    def test_workflow_runs_improvement_cycle(self):
        """Test that workflow runs improvement cycle script."""
        self.assertIsNotNone(self.workflow_content)
        self.assertIn(
            "start_improvement_cycle.sh",
            self.workflow_content,
            "Workflow should run start_improvement_cycle.sh"
        )


if __name__ == '__main__':
    unittest.main()
