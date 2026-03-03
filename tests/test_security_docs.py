"""
Tests for repository security documentation.

This module tests the presence and quality of SECURITY.md file.
"""

import unittest
from pathlib import Path


class TestSecurityDocumentation(unittest.TestCase):
    """Test cases for SECURITY.md documentation."""

    def setUp(self):
        """Set up test fixtures."""
        # tests/ is in root, so we just need root directory
        self.root_dir = Path(__file__).parent.parent
        self.security_file = self.root_dir / "SECURITY.md"
        self.security_content = None
        
        if self.security_file.exists():
            self.security_content = self.security_file.read_text(encoding='utf-8')

    def test_security_file_exists(self):
        """Test that SECURITY.md exists in repository root."""
        self.assertTrue(
            self.security_file.exists(),
            f"SECURITY.md not found at {self.security_file}"
        )

    def test_security_file_not_empty(self):
        """Test that SECURITY.md is not empty."""
        self.assertIsNotNone(
            self.security_content,
            "SECURITY.md file is empty"
        )
        self.assertGreater(
            len(self.security_content),
            100,
            "SECURITY.md file is too short (< 100 characters)"
        )

    def test_security_has_supported_versions(self):
        """Test that SECURITY.md contains supported versions section."""
        self.assertIsNotNone(
            self.security_content,
            "SECURITY.md file does not exist"
        )
        self.assertIn(
            "Supported Versions",
            self.security_content,
            "SECURITY.md missing 'Supported Versions' section"
        )

    def test_security_has_reporting_process(self):
        """Test that SECURITY.md contains vulnerability reporting process."""
        self.assertIsNotNone(
            self.security_content,
            "SECURITY.md file does not exist"
        )
        reporting_keywords = [
            "Reporting a Vulnerability",
            "Reporting Vulnerability",
            "Report a Vulnerability",
            "reporting a vulnerability"
        ]
        has_reporting = any(
            keyword in self.security_content 
            for keyword in reporting_keywords
        )
        self.assertTrue(
            has_reporting,
            "SECURITY.md missing vulnerability reporting section"
        )

    def test_security_has_contact_method(self):
        """Test that SECURITY.md contains contact method for reporting."""
        self.assertIsNotNone(
            self.security_content,
            "SECURITY.md file does not exist"
        )
        contact_keywords = [
            "email",
            "mailto:",
            "@",
            "contact",
            "report"
        ]
        has_contact = any(
            keyword in self.security_content.lower()
            for keyword in contact_keywords
        )
        self.assertTrue(
            has_contact,
            "SECURITY.md missing contact method for reporting"
        )

    def test_security_has_response_timeline(self):
        """Test that SECURITY.md contains response timeline."""
        self.assertIsNotNone(
            self.security_content,
            "SECURITY.md file does not exist"
        )
        timeline_keywords = [
            "48 hours",
            "24 hours",
            "72 hours",
            "within",
            "response",
            "reply"
        ]
        has_timeline = any(
            keyword in self.security_content.lower()
            for keyword in timeline_keywords
        )
        self.assertTrue(
            has_timeline,
            "SECURITY.md missing response timeline"
        )

    def test_security_has_best_practices(self):
        """Test that SECURITY.md contains security best practices."""
        self.assertIsNotNone(
            self.security_content,
            "SECURITY.md file does not exist"
        )
        best_practice_keywords = [
            "Best Practices",
            "Security Best Practices",
            "best practices",
            "When using Conductor"
        ]
        has_best_practices = any(
            keyword in self.security_content
            for keyword in best_practice_keywords
        )
        self.assertTrue(
            has_best_practices,
            "SECURITY.md missing security best practices section"
        )

    def test_security_no_hardcoded_secrets(self):
        """Test that SECURITY.md contains no hardcoded secrets."""
        self.assertIsNotNone(
            self.security_content,
            "SECURITY.md file does not exist"
        )
        
        # Check for potential secrets (basic patterns)
        secret_patterns = [
            "api_key =",
            "apikey =",
            "api-key =",
            "password =",
            "secret =",
            "token =",
        ]
        
        has_secrets = any(
            pattern in self.security_content.lower()
            for pattern in secret_patterns
        )
        self.assertFalse(
            has_secrets,
            "SECURITY.md appears to contain hardcoded secrets"
        )


class TestSecurityFileLocation(unittest.TestCase):
    """Test SECURITY.md file location and accessibility."""

    def test_security_in_root(self):
        """Test that SECURITY.md is in repository root."""
        root_dir = Path(__file__).parent.parent
        security_file = root_dir / "SECURITY.md"
        
        self.assertTrue(
            security_file.exists(),
            f"SECURITY.md should be in repository root, found at: {security_file}"
        )
        
        # Verify it's not in a subdirectory
        self.assertEqual(
            security_file.parent,
            root_dir,
            "SECURITY.md should be in repository root, not in a subdirectory"
        )


if __name__ == '__main__':
    unittest.main()
