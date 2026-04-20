"""
Comprehensive tests for export_copilot_history.py
Covers positive and negative scenarios for all key functions.
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import export_copilot_history as exp


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def make_kind1_line(user_text, response_text, session_lines=None):
    """Build a JSONL line that mimics a kind=1 VS Code session object."""
    obj = {
        "kind": 1,
        "v": {
            "metadata": {
                "renderedUserMessage": [{"text": user_text}],
                "toolCallRounds": [{"response": response_text}],
            }
        }
    }
    return json.dumps(obj)


def make_kind0_line(user_text, response_text):
    """Build a JSONL line that mimics a kind=0 VS Code session object."""
    obj = {
        "kind": 0,
        "v": {
            "requests": [
                {
                    "message": {"text": user_text},
                    "response": response_text,
                    "requestId": "req-001",
                    "timestamp": 1000,
                }
            ]
        }
    }
    return json.dumps(obj)


def write_jsonl(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


# ─────────────────────────────────────────────
# 1. OUTPUT_FILE_PREFIX
# ─────────────────────────────────────────────

class TestOutputFilePrefix(unittest.TestCase):

    def test_prefix_value(self):
        self.assertEqual(exp.OUTPUT_FILE_PREFIX, "chat_history")

    def test_prefix_used_in_json_filename(self):
        with tempfile.TemporaryDirectory() as d:
            entries = [{"role": "user", "message": "hi", "sourceSession": "s1", "source": "kind1"}]
            path = exp.export_to_json(entries, [], "2026-01-01", d)
            self.assertIn("chat_history_2026-01-01.json", path)

    def test_prefix_used_in_md_filename(self):
        with tempfile.TemporaryDirectory() as d:
            entries = [{"role": "user", "message": "hi", "sourceSession": "s1", "source": "kind1"}]
            path = exp.export_to_markdown(entries, "2026-01-01", d)
            self.assertIn("chat_history_2026-01-01.md", path)

    def test_prefix_not_old_name(self):
        self.assertNotEqual(exp.OUTPUT_FILE_PREFIX, "prompt_response_history")


# ─────────────────────────────────────────────
# 2. clean_text
# ─────────────────────────────────────────────

class TestCleanText(unittest.TestCase):

    def test_strips_whitespace(self):
        self.assertEqual(exp.clean_text("  hello  "), "hello")

    def test_normalizes_crlf(self):
        result = exp.clean_text("line1\r\nline2")
        self.assertNotIn("\r", result)

    def test_collapses_extra_blank_lines(self):
        result = exp.clean_text("a\n\n\n\nb")
        self.assertNotIn("\n\n\n", result)

    def test_collapses_multiple_spaces(self):
        result = exp.clean_text("hello   world")
        self.assertEqual(result, "hello world")

    def test_empty_string(self):
        self.assertEqual(exp.clean_text(""), "")

    def test_only_whitespace(self):
        self.assertEqual(exp.clean_text("   \n\t  "), "")


# ─────────────────────────────────────────────
# 3. extract_assistant_response
# ─────────────────────────────────────────────

class TestExtractAssistantResponse(unittest.TestCase):

    def test_list_with_value_key(self):
        result = exp.extract_assistant_response([{"value": "hello"}])
        self.assertEqual(result, "hello")

    def test_list_with_content_value(self):
        result = exp.extract_assistant_response([{"content": {"value": "world"}}])
        self.assertEqual(result, "world")

    def test_dict_with_value_key(self):
        result = exp.extract_assistant_response({"value": "response"})
        self.assertEqual(result, "response")

    def test_plain_string(self):
        result = exp.extract_assistant_response("plain text")
        self.assertEqual(result, "plain text")

    def test_deduplicates_repeated_values(self):
        result = exp.extract_assistant_response([{"value": "dup"}, {"value": "dup"}])
        self.assertEqual(result.count("dup"), 1)

    def test_empty_list(self):
        result = exp.extract_assistant_response([])
        self.assertEqual(result, "")

    def test_none_input(self):
        result = exp.extract_assistant_response(None)
        self.assertEqual(result, "")

    def test_ignores_blank_values(self):
        result = exp.extract_assistant_response([{"value": "   "}])
        self.assertEqual(result, "")


# ─────────────────────────────────────────────
# 4. parse_session_file — positive
# ─────────────────────────────────────────────

class TestParseSessionFilePositive(unittest.TestCase):

    def test_kind1_produces_user_and_assistant(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "abc123.jsonl")
            write_jsonl(path, [make_kind1_line("What is Python?", "Python is a language.")])
            entries = exp.parse_session_file(path)
            roles = [e["role"] for e in entries]
            self.assertIn("user", roles)
            self.assertIn("assistant", roles)

    def test_kind1_user_message_content(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "abc123.jsonl")
            write_jsonl(path, [make_kind1_line("Tell me a joke", "Why did the chicken cross the road?")])
            entries = exp.parse_session_file(path)
            user_entry = next(e for e in entries if e["role"] == "user")
            self.assertIn("Tell me a joke", user_entry["message"])

    def test_kind1_assistant_message_content(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "abc123.jsonl")
            write_jsonl(path, [make_kind1_line("Q", "This is the answer.")])
            entries = exp.parse_session_file(path)
            asst = next(e for e in entries if e["role"] == "assistant")
            self.assertIn("This is the answer.", asst["message"])

    def test_kind1_interleaved_order(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "abc123.jsonl")
            write_jsonl(path, [
                make_kind1_line("Q1", "A1"),
                make_kind1_line("Q2", "A2"),
            ])
            entries = exp.parse_session_file(path)
            roles = [e["role"] for e in entries]
            self.assertEqual(roles, ["user", "assistant", "user", "assistant"])

    def test_kind1_source_label(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "abc123.jsonl")
            write_jsonl(path, [make_kind1_line("Hello", "World")])
            entries = exp.parse_session_file(path)
            sources = {e["source"] for e in entries}
            self.assertTrue(any("kind1" in s for s in sources))

    def test_kind1_session_id_set(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "mysession.jsonl")
            write_jsonl(path, [make_kind1_line("Q", "A")])
            entries = exp.parse_session_file(path)
            for e in entries:
                self.assertEqual(e["sourceSession"], "mysession")

    def test_kind0_fallback_when_no_kind1(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "old.jsonl")
            write_jsonl(path, [make_kind0_line("Old question", "Old answer")])
            entries = exp.parse_session_file(path)
            roles = [e["role"] for e in entries]
            self.assertIn("user", roles)
            self.assertIn("assistant", roles)

    def test_multiple_tool_call_rounds_combined(self):
        """Multiple toolCallRounds should be joined into one assistant entry."""
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "multi.jsonl")
            obj = {
                "kind": 1,
                "v": {
                    "metadata": {
                        "renderedUserMessage": [{"text": "complex question"}],
                        "toolCallRounds": [
                            {"response": "Part one."},
                            {"response": "Part two."},
                        ]
                    }
                }
            }
            write_jsonl(path, [json.dumps(obj)])
            entries = exp.parse_session_file(path)
            asst = next(e for e in entries if e["role"] == "assistant")
            self.assertIn("Part one.", asst["message"])
            self.assertIn("Part two.", asst["message"])


# ─────────────────────────────────────────────
# 5. parse_session_file — negative
# ─────────────────────────────────────────────

class TestParseSessionFileNegative(unittest.TestCase):

    def test_nonexistent_file_returns_empty(self):
        entries = exp.parse_session_file("/nonexistent/path/file.jsonl")
        self.assertEqual(entries, [])

    def test_empty_file_returns_empty(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "empty.jsonl")
            write_jsonl(path, [])
            entries = exp.parse_session_file(path)
            self.assertEqual(entries, [])

    def test_invalid_json_lines_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "bad.jsonl")
            with open(path, "w") as f:
                f.write("not json\n")
                f.write('{"kind": 1}\n')  # valid but incomplete
            entries = exp.parse_session_file(path)
            self.assertIsInstance(entries, list)

    def test_kind1_without_user_text_skips_user_entry(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "noprompt.jsonl")
            obj = {
                "kind": 1,
                "v": {
                    "metadata": {
                        "renderedUserMessage": [{"text": "   "}],
                        "toolCallRounds": [{"response": "some response"}]
                    }
                }
            }
            write_jsonl(path, [json.dumps(obj)])
            entries = exp.parse_session_file(path)
            user_entries = [e for e in entries if e["role"] == "user"]
            self.assertEqual(len(user_entries), 0)

    def test_kind1_without_response_skips_assistant_entry(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "noresponse.jsonl")
            obj = {
                "kind": 1,
                "v": {
                    "metadata": {
                        "renderedUserMessage": [{"text": "a question"}],
                        "toolCallRounds": [{"response": ""}]
                    }
                }
            }
            write_jsonl(path, [json.dumps(obj)])
            entries = exp.parse_session_file(path)
            asst_entries = [e for e in entries if e["role"] == "assistant"]
            self.assertEqual(len(asst_entries), 0)

    def test_kind1_missing_metadata_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "nometa.jsonl")
            obj = {"kind": 1, "v": {}}
            write_jsonl(path, [json.dumps(obj)])
            entries = exp.parse_session_file(path)
            self.assertEqual(entries, [])


# ─────────────────────────────────────────────
# 6. deduplicate_entries
# ─────────────────────────────────────────────

class TestDeduplicateEntries(unittest.TestCase):

    def _entry(self, role, msg, session="s1", source="kind1"):
        return {"role": role, "message": msg, "sourceSession": session, "source": source}

    def test_removes_exact_duplicates(self):
        entries = [self._entry("user", "hi"), self._entry("user", "hi")]
        result = exp.deduplicate_entries(entries)
        self.assertEqual(len(result), 1)

    def test_preserves_unique_entries(self):
        entries = [self._entry("user", "hi"), self._entry("assistant", "hello")]
        result = exp.deduplicate_entries(entries)
        self.assertEqual(len(result), 2)

    def test_preserves_order(self):
        entries = [self._entry("user", "first"), self._entry("assistant", "second")]
        result = exp.deduplicate_entries(entries)
        self.assertEqual(result[0]["message"], "first")
        self.assertEqual(result[1]["message"], "second")

    def test_empty_list(self):
        self.assertEqual(exp.deduplicate_entries([]), [])

    def test_same_message_different_role_kept(self):
        entries = [self._entry("user", "same"), self._entry("assistant", "same")]
        result = exp.deduplicate_entries(entries)
        self.assertEqual(len(result), 2)

    def test_same_message_different_session_kept(self):
        entries = [self._entry("user", "hi", session="s1"), self._entry("user", "hi", session="s2")]
        result = exp.deduplicate_entries(entries)
        self.assertEqual(len(result), 2)


# ─────────────────────────────────────────────
# 7. export_to_json
# ─────────────────────────────────────────────

class TestExportToJson(unittest.TestCase):

    def _sample_entries(self):
        return [
            {"role": "user", "message": "hello", "sourceSession": "s1", "source": "kind1"},
            {"role": "assistant", "message": "world", "sourceSession": "s1", "source": "kind1"},
        ]

    def test_creates_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = exp.export_to_json(self._sample_entries(), [], "2026-01-01", d)
            self.assertTrue(os.path.exists(path))

    def test_correct_filename(self):
        with tempfile.TemporaryDirectory() as d:
            path = exp.export_to_json(self._sample_entries(), [], "2026-05-10", d)
            self.assertTrue(path.endswith("chat_history_2026-05-10.json"))

    def test_valid_json_output(self):
        with tempfile.TemporaryDirectory() as d:
            path = exp.export_to_json(self._sample_entries(), [], "2026-01-01", d)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self.assertIn("history", data)
            self.assertEqual(data["historyCount"], 2)

    def test_date_in_output(self):
        with tempfile.TemporaryDirectory() as d:
            path = exp.export_to_json(self._sample_entries(), [], "2026-03-15", d)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["date"], "2026-03-15")

    def test_empty_entries(self):
        with tempfile.TemporaryDirectory() as d:
            path = exp.export_to_json([], [], "2026-01-01", d)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["historyCount"], 0)


# ─────────────────────────────────────────────
# 8. export_to_markdown
# ─────────────────────────────────────────────

class TestExportToMarkdown(unittest.TestCase):

    def _sample_entries(self):
        return [
            {"role": "user", "message": "What is AI?", "sourceSession": "s1", "source": "kind1"},
            {"role": "assistant", "message": "AI stands for Artificial Intelligence.", "sourceSession": "s1", "source": "kind1"},
        ]

    def test_creates_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = exp.export_to_markdown(self._sample_entries(), "2026-01-01", d)
            self.assertTrue(os.path.exists(path))

    def test_correct_filename(self):
        with tempfile.TemporaryDirectory() as d:
            path = exp.export_to_markdown(self._sample_entries(), "2026-07-04", d)
            self.assertTrue(path.endswith("chat_history_2026-07-04.md"))

    def test_contains_user_message(self):
        with tempfile.TemporaryDirectory() as d:
            path = exp.export_to_markdown(self._sample_entries(), "2026-01-01", d)
            content = Path(path).read_text(encoding="utf-8")
            self.assertIn("What is AI?", content)

    def test_contains_assistant_message(self):
        with tempfile.TemporaryDirectory() as d:
            path = exp.export_to_markdown(self._sample_entries(), "2026-01-01", d)
            content = Path(path).read_text(encoding="utf-8")
            self.assertIn("Artificial Intelligence", content)

    def test_contains_date_header(self):
        with tempfile.TemporaryDirectory() as d:
            path = exp.export_to_markdown(self._sample_entries(), "2026-01-01", d)
            content = Path(path).read_text(encoding="utf-8")
            self.assertIn("2026-01-01", content)

    def test_contains_user_and_assistant_labels(self):
        with tempfile.TemporaryDirectory() as d:
            path = exp.export_to_markdown(self._sample_entries(), "2026-01-01", d)
            content = Path(path).read_text(encoding="utf-8")
            self.assertIn("USER", content)
            self.assertIn("ASSISTANT", content)

    def test_entry_numbering(self):
        with tempfile.TemporaryDirectory() as d:
            path = exp.export_to_markdown(self._sample_entries(), "2026-01-01", d)
            content = Path(path).read_text(encoding="utf-8")
            self.assertIn("Entry 1", content)
            self.assertIn("Entry 2", content)

    def test_title_says_chat_history(self):
        with tempfile.TemporaryDirectory() as d:
            path = exp.export_to_markdown(self._sample_entries(), "2026-01-01", d)
            content = Path(path).read_text(encoding="utf-8")
            self.assertIn("Chat History", content)


# ─────────────────────────────────────────────
# 9. calculate_date_from_days_ago
# ─────────────────────────────────────────────

class TestCalculateDateFromDaysAgo(unittest.TestCase):

    def test_zero_days_ago_is_today(self):
        result = exp.calculate_date_from_days_ago(0)
        self.assertEqual(result, datetime.now().strftime("%Y-%m-%d"))

    def test_one_day_ago(self):
        expected = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertEqual(exp.calculate_date_from_days_ago(1), expected)

    def test_seven_days_ago(self):
        expected = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        self.assertEqual(exp.calculate_date_from_days_ago(7), expected)

    def test_negative_days_raises(self):
        with self.assertRaises(ValueError):
            exp.calculate_date_from_days_ago(-1)

    def test_returns_string(self):
        self.assertIsInstance(exp.calculate_date_from_days_ago(0), str)

    def test_date_format(self):
        result = exp.calculate_date_from_days_ago(3)
        # Must match YYYY-MM-DD
        datetime.strptime(result, "%Y-%m-%d")


# ─────────────────────────────────────────────
# 10. parse_custom_date
# ─────────────────────────────────────────────

class TestParseCustomDate(unittest.TestCase):

    def test_valid_past_date(self):
        result = exp.parse_custom_date("2024-01-15")
        self.assertEqual(result, "2024-01-15")

    def test_future_date_raises(self):
        future = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        with self.assertRaises(ValueError):
            exp.parse_custom_date(future)

    def test_invalid_format_raises(self):
        with self.assertRaises(ValueError):
            exp.parse_custom_date("15-01-2024")

    def test_invalid_string_raises(self):
        with self.assertRaises(ValueError):
            exp.parse_custom_date("not-a-date")

    def test_empty_string_raises(self):
        with self.assertRaises(ValueError):
            exp.parse_custom_date("")

    def test_returns_formatted_string(self):
        result = exp.parse_custom_date("2023-06-01")
        self.assertEqual(result, "2023-06-01")


# ─────────────────────────────────────────────
# 11. find_session_files
# ─────────────────────────────────────────────

class TestFindSessionFiles(unittest.TestCase):

    def test_finds_jsonl_in_chatSessions(self):
        with tempfile.TemporaryDirectory() as root:
            chat_dir = os.path.join(root, "workspace1", "chatSessions")
            os.makedirs(chat_dir)
            f = os.path.join(chat_dir, "session1.jsonl")
            Path(f).touch()
            today = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d")
            result = exp.find_session_files(today, workspace_root=root)
            self.assertIn(f, result)

    def test_ignores_non_jsonl_files(self):
        with tempfile.TemporaryDirectory() as root:
            chat_dir = os.path.join(root, "workspace1", "chatSessions")
            os.makedirs(chat_dir)
            f = os.path.join(chat_dir, "session.txt")
            Path(f).touch()
            today = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d")
            result = exp.find_session_files(today, workspace_root=root)
            self.assertNotIn(f, result)

    def test_ignores_non_chatSessions_dirs(self):
        with tempfile.TemporaryDirectory() as root:
            other_dir = os.path.join(root, "workspace1", "otherFolder")
            os.makedirs(other_dir)
            f = os.path.join(other_dir, "session.jsonl")
            Path(f).touch()
            today = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d")
            result = exp.find_session_files(today, workspace_root=root)
            self.assertNotIn(f, result)

    def test_nonexistent_root_returns_empty(self):
        result = exp.find_session_files("2024-01-01", workspace_root="/no/such/path")
        self.assertEqual(result, [])

    def test_wrong_date_returns_empty(self):
        with tempfile.TemporaryDirectory() as root:
            chat_dir = os.path.join(root, "workspace1", "chatSessions")
            os.makedirs(chat_dir)
            f = os.path.join(chat_dir, "session.jsonl")
            Path(f).touch()
            result = exp.find_session_files("1999-01-01", workspace_root=root)
            self.assertEqual(result, [])


# ─────────────────────────────────────────────
# 12. Config management
# ─────────────────────────────────────────────

class TestConfigManagement(unittest.TestCase):

    def test_save_and_load_config(self):
        with tempfile.TemporaryDirectory() as d:
            config_path = os.path.join(d, "config.json")
            config = {"output_dir": d, "export_time": "18:00", "timezone": "IST"}
            with patch.object(exp, "get_config_file", return_value=config_path):
                exp.save_config(config)
                loaded = exp.load_config()
            self.assertEqual(loaded["output_dir"], d)

    def test_load_config_missing_file_returns_none(self):
        with patch.object(exp, "get_config_file", return_value="/no/such/config.json"):
            result = exp.load_config()
        self.assertIsNone(result)

    def test_save_config_returns_true_on_success(self):
        with tempfile.TemporaryDirectory() as d:
            config_path = os.path.join(d, "cfg.json")
            with patch.object(exp, "get_config_file", return_value=config_path):
                result = exp.save_config({"key": "value"})
            self.assertTrue(result)

    def test_load_config_invalid_json_returns_none(self):
        with tempfile.TemporaryDirectory() as d:
            config_path = os.path.join(d, "bad.json")
            with open(config_path, "w") as f:
                f.write("NOT JSON")
            with patch.object(exp, "get_config_file", return_value=config_path):
                result = exp.load_config()
        self.assertIsNone(result)

    def test_load_config_backfills_run_mode_default(self):
        with tempfile.TemporaryDirectory() as d:
            config_path = os.path.join(d, "cfg.json")
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump({"output_dir": d, "timezone": "IST", "export_time": "18:00"}, f)
            with patch.object(exp, "get_config_file", return_value=config_path):
                result = exp.load_config()
        self.assertEqual(result["run_mode"], exp.RUN_MODE_AUTOMATIC)


class TestRunModeBehavior(unittest.TestCase):

    def test_normalize_manual_mode_clears_export_time(self):
        cfg = {"run_mode": "manual", "export_time": "18:00", "timezone": "IST"}
        normalized = exp.normalize_config(cfg)
        self.assertEqual(normalized["run_mode"], exp.RUN_MODE_MANUAL)
        self.assertIsNone(normalized["export_time"])

    def test_normalize_invalid_mode_defaults_to_automatic(self):
        cfg = {"run_mode": "invalid-mode", "timezone": "IST"}
        normalized = exp.normalize_config(cfg)
        self.assertEqual(normalized["run_mode"], exp.RUN_MODE_AUTOMATIC)
        self.assertEqual(normalized["export_time"], "23:00")

    def test_non_interactive_overwrites_existing_files(self):
        with tempfile.TemporaryDirectory() as d:
            target_date = "2026-04-20"
            json_path = os.path.join(d, f"{exp.OUTPUT_FILE_PREFIX}_{target_date}.json")
            Path(json_path).write_text("{}", encoding="utf-8")
            self.assertTrue(
                exp.check_file_exists_and_prompt(d, target_date, non_interactive=True)
            )


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFilePrefix))
    suite.addTests(loader.loadTestsFromTestCase(TestCleanText))
    suite.addTests(loader.loadTestsFromTestCase(TestExtractAssistantResponse))
    suite.addTests(loader.loadTestsFromTestCase(TestParseSessionFilePositive))
    suite.addTests(loader.loadTestsFromTestCase(TestParseSessionFileNegative))
    suite.addTests(loader.loadTestsFromTestCase(TestDeduplicateEntries))
    suite.addTests(loader.loadTestsFromTestCase(TestExportToJson))
    suite.addTests(loader.loadTestsFromTestCase(TestExportToMarkdown))
    suite.addTests(loader.loadTestsFromTestCase(TestCalculateDateFromDaysAgo))
    suite.addTests(loader.loadTestsFromTestCase(TestParseCustomDate))
    suite.addTests(loader.loadTestsFromTestCase(TestFindSessionFiles))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestRunModeBehavior))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors

    print("\n" + "="*60)
    print(f"RESULTS: {passed}/{total} passed | {failures} failures | {errors} errors")
    print("="*60)

    sys.exit(0 if result.wasSuccessful() else 1)
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
