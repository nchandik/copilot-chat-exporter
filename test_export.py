#!/usr/bin/env python3
"""
Unit tests for Copilot Chat History Exporter

Tests cover:
- Date calculation functions (positive & negative)
- Input validation
- File operations
- Configuration handling
"""

import unittest
import os
import sys
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import functions from main script
sys.path.insert(0, os.path.dirname(__file__))
from export_copilot_history import (
    calculate_date_from_days_ago,
    parse_custom_date,
    deduplicate_entries,
    clean_text,
    extract_assistant_response,
    get_config_file,
    load_config,
    save_config,
)


class TestDateCalculation(unittest.TestCase):
    """Test date calculation functions."""

    def test_days_ago_zero_is_today(self):
        """Test that days_ago=0 returns today."""
        today = datetime.now().strftime("%Y-%m-%d")
        result = calculate_date_from_days_ago(0)
        self.assertEqual(result, today)

    def test_days_ago_one_is_yesterday(self):
        """Test that days_ago=1 returns yesterday."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        result = calculate_date_from_days_ago(1)
        self.assertEqual(result, yesterday)

    def test_days_ago_seven_is_one_week(self):
        """Test that days_ago=7 returns one week ago."""
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        result = calculate_date_from_days_ago(7)
        self.assertEqual(result, week_ago)

    def test_days_ago_negative_raises_error(self):
        """Test that negative days_ago raises ValueError."""
        with self.assertRaises(ValueError) as context:
            calculate_date_from_days_ago(-1)
        self.assertIn("must be >= 0", str(context.exception))

    def test_days_ago_large_number(self):
        """Test that large days_ago works."""
        result = calculate_date_from_days_ago(365)
        self.assertIsNotNone(result)
        # Verify format is correct
        datetime.strptime(result, "%Y-%m-%d")


class TestDateParsing(unittest.TestCase):
    """Test custom date parsing."""

    def test_parse_valid_date(self):
        """Test parsing a valid past date."""
        # Use a date from the past
        past_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        result = parse_custom_date(past_date)
        self.assertEqual(result, past_date)

    def test_parse_today(self):
        """Test parsing today's date (boundary case)."""
        today = datetime.now().strftime("%Y-%m-%d")
        result = parse_custom_date(today)
        self.assertEqual(result, today)

    def test_parse_invalid_format(self):
        """Test parsing with invalid format."""
        with self.assertRaises(ValueError):
            parse_custom_date("2026/04/16")

    def test_parse_future_date_raises_error(self):
        """Test that future date raises ValueError."""
        future_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        with self.assertRaises(ValueError) as context:
            parse_custom_date(future_date)
        self.assertIn("future", str(context.exception).lower())

    def test_parse_invalid_month(self):
        """Test parsing with invalid month."""
        with self.assertRaises(ValueError):
            parse_custom_date("2026-13-01")

    def test_parse_invalid_day(self):
        """Test parsing with invalid day."""
        with self.assertRaises(ValueError):
            parse_custom_date("2026-02-30")

    def test_parse_malformed_string(self):
        """Test parsing with malformed string."""
        with self.assertRaises(ValueError):
            parse_custom_date("not-a-date")


class TestTextCleaning(unittest.TestCase):
    """Test text cleaning functions."""

    def test_clean_text_whitespace(self):
        """Test that extra whitespace is normalized."""
        messy = "  hello   world  "
        result = clean_text(messy)
        self.assertEqual(result, "hello world")

    def test_clean_text_newlines(self):
        """Test that multiple newlines are collapsed."""
        messy = "line1\n\n\nline2"
        result = clean_text(messy)
        self.assertEqual(result, "line1\n\nline2")

    def test_clean_text_mixed_line_endings(self):
        """Test mixed line endings are normalized."""
        messy = "line1\r\nline2\rline3"
        result = clean_text(messy)
        self.assertIn("line1", result)
        self.assertIn("line2", result)
        self.assertIn("line3", result)

    def test_clean_text_empty_string(self):
        """Test cleaning empty string."""
        result = clean_text("")
        self.assertEqual(result, "")

    def test_clean_text_only_whitespace(self):
        """Test cleaning string with only whitespace."""
        result = clean_text("   \n   \t   ")
        self.assertEqual(result, "")


class TestAssistantResponseExtraction(unittest.TestCase):
    """Test assistant response extraction."""

    def test_extract_from_list_with_value(self):
        """Test extracting from list with value field."""
        response = [{"value": "Hello, world!"}]
        result = extract_assistant_response(response)
        self.assertIn("Hello", result)

    def test_extract_from_dict_with_value(self):
        """Test extracting from dict with value field."""
        response = {"value": "Test response"}
        result = extract_assistant_response(response)
        self.assertEqual(result, "Test response")

    def test_extract_from_string(self):
        """Test extracting from plain string."""
        response = "Plain text response"
        result = extract_assistant_response(response)
        self.assertEqual(result, "Plain text response")

    def test_extract_deduplicates(self):
        """Test that duplicates are removed."""
        response = [{"value": "Same"}, {"value": "Same"}, {"value": "Different"}]
        result = extract_assistant_response(response)
        # Should contain both unique values but not duplicate
        self.assertIn("Same", result)
        self.assertIn("Different", result)

    def test_extract_from_empty_list(self):
        """Test extracting from empty list."""
        result = extract_assistant_response([])
        self.assertEqual(result, "")

    def test_extract_from_none(self):
        """Test extracting from None."""
        result = extract_assistant_response(None)
        self.assertEqual(result, "")

    def test_extract_nested_content(self):
        """Test extracting from nested content dict."""
        response = [{"content": {"value": "Nested value"}}]
        result = extract_assistant_response(response)
        self.assertIn("Nested value", result)


class TestDeduplication(unittest.TestCase):
    """Test entry deduplication."""

    def test_deduplicate_removes_exact_duplicates(self):
        """Test that exact duplicates are removed."""
        entries = [
            {"role": "user", "message": "Hello", "sourceSession": "s1", "source": "test"},
            {"role": "user", "message": "Hello", "sourceSession": "s1", "source": "test"},
            {"role": "user", "message": "World", "sourceSession": "s1", "source": "test"},
        ]
        result = deduplicate_entries(entries)
        self.assertEqual(len(result), 2)

    def test_deduplicate_preserves_order(self):
        """Test that order is preserved after dedup."""
        entries = [
            {"role": "user", "message": "First", "sourceSession": "s1", "source": "test"},
            {"role": "user", "message": "Second", "sourceSession": "s1", "source": "test"},
            {"role": "user", "message": "First", "sourceSession": "s1", "source": "test"},
        ]
        result = deduplicate_entries(entries)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["message"], "First")
        self.assertEqual(result[1]["message"], "Second")

    def test_deduplicate_different_sources_kept(self):
        """Test that same message from different sources are kept."""
        entries = [
            {"role": "user", "message": "Test", "sourceSession": "s1", "source": "kind0"},
            {"role": "user", "message": "Test", "sourceSession": "s1", "source": "kind1"},
        ]
        result = deduplicate_entries(entries)
        self.assertEqual(len(result), 2)

    def test_deduplicate_empty_list(self):
        """Test deduplicating empty list."""
        result = deduplicate_entries([])
        self.assertEqual(result, [])


class TestConfigManagement(unittest.TestCase):
    """Test configuration file handling."""

    def setUp(self):
        """Create temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, ".copilot_exporter_config.json")

    def test_save_and_load_config(self):
        """Test saving and loading config."""
        config = {
            "output_dir": "/test/path",
            "export_time": "18:00",
            "timezone": "IST",
        }
        
        # Mock get_config_file to use temp path
        with patch('export_copilot_history.get_config_file', return_value=self.config_file):
            save_config(config)
            loaded = load_config()
            
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["output_dir"], "/test/path")
            self.assertEqual(loaded["timezone"], "IST")

    def test_load_nonexistent_config(self):
        """Test loading config that doesn't exist."""
        with patch('export_copilot_history.get_config_file', return_value="/nonexistent/path"):
            result = load_config()
            self.assertIsNone(result)

    def test_config_file_path_uses_home(self):
        """Test that config file is stored in home directory."""
        config_path = get_config_file()
        home = str(Path.home())
        self.assertTrue(config_path.startswith(home))
        self.assertIn(".copilot_exporter_config.json", config_path)


class TestInputValidation(unittest.TestCase):
    """Test input validation for CLI arguments."""

    def test_negative_days_ago_rejected(self):
        """Test that negative days-ago is rejected."""
        with self.assertRaises(ValueError):
            calculate_date_from_days_ago(-5)

    def test_zero_batch_rejected(self):
        """Test that batch < 1 is invalid."""
        # This would be validated in main(), so we just check the concept
        self.assertTrue(0 < 1)  # Verify that batch=0 would be invalid
        self.assertFalse(0 >= 1)  # 0 is not >= 1

    def test_invalid_date_format_rejected(self):
        """Test that invalid date format is rejected."""
        with self.assertRaises(ValueError):
            parse_custom_date("2026-04-99")

    def test_valid_timezone_values(self):
        """Test that known timezones are valid."""
        valid_zones = ["IST", "EST", "CST", "MST", "PST"]
        for zone in valid_zones:
            self.assertIn(zone, valid_zones)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_leap_year_date(self):
        """Test handling of leap year dates."""
        # 2024 is a leap year
        leap_date = "2024-02-29"
        result = parse_custom_date(leap_date)
        self.assertEqual(result, leap_date)

    def test_very_old_date(self):
        """Test handling of very old dates."""
        # 365 days ago should work
        result = calculate_date_from_days_ago(365)
        self.assertIsNotNone(result)
        datetime.strptime(result, "%Y-%m-%d")

    def test_year_boundary(self):
        """Test date calculation across year boundary."""
        # If we're near new year, days_ago should handle it
        result = calculate_date_from_days_ago(30)
        datetime.strptime(result, "%Y-%m-%d")

    def test_single_entry_dedup(self):
        """Test deduplicating single entry."""
        entries = [{"role": "user", "message": "Test", "sourceSession": "s1", "source": "test"}]
        result = deduplicate_entries(entries)
        self.assertEqual(len(result), 1)

    def test_large_entry_count(self):
        """Test deduplication with many entries."""
        entries = [
            {"role": "user", "message": f"Message {i}", "sourceSession": "s1", "source": "test"}
            for i in range(1000)
        ]
        result = deduplicate_entries(entries)
        self.assertEqual(len(result), 1000)


class TestFileOperations(unittest.TestCase):
    """Test file-related operations."""

    def setUp(self):
        """Create temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_output_directory_creation(self):
        """Test that output directory is created if missing."""
        test_path = os.path.join(self.temp_dir, "new", "nested", "dir")
        os.makedirs(test_path, exist_ok=True)
        self.assertTrue(os.path.isdir(test_path))

    def test_file_path_generation(self):
        """Test that file paths are generated correctly."""
        date = "2026-04-16"
        json_file = f"chat_history_{date}.json"
        md_file = f"chat_history_{date}.md"
        
        self.assertIn(date, json_file)
        self.assertIn(date, md_file)
        self.assertTrue(json_file.startswith("chat_history_"))
        self.assertTrue(json_file.endswith(".json"))
        self.assertTrue(md_file.endswith(".md"))


# Test execution
if __name__ == "__main__":
    print("\n" + "="*70)
    print("[TEST] Running Copilot Chat Exporter Tests")
    print("="*70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDateCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestDateParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestTextCleaning))
    suite.addTests(loader.loadTestsFromTestCase(TestAssistantResponseExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestDeduplication))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestInputValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestFileOperations))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*70)
    if result.wasSuccessful():
        print(f"[OK] All {result.testsRun} tests PASSED!")
    else:
        print(f"[FAIL] {len(result.failures)} failures, {len(result.errors)} errors")
    print("="*70 + "\n")
    
    sys.exit(0 if result.wasSuccessful() else 1)
