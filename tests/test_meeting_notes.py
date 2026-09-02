import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from meeting_notes import (  # noqa: E402
    MeetingNotesError,
    parse_notes,
    read_notes,
    save_summary,
)


SAMPLE_NOTES = """Title: Checkout Reliability Review
Owner: Riya
Date: 2026-08-24
Attendees: Riya, Sam, Noor
Decisions: Add retry logging; create a payment failure dashboard
Actions: Sam|Add structured logs|2026-08-26; Noor|Draft dashboard|2026-08-28
"""


class ParseNotesTests(unittest.TestCase):
    def test_parse_notes_extracts_required_shape(self) -> None:
        summary = parse_notes(SAMPLE_NOTES)

        self.assertEqual(summary["title"], "Checkout Reliability Review")
        self.assertEqual(summary["owner"], "Riya")
        self.assertEqual(summary["date"], "2026-08-24")
        self.assertEqual(summary["attendees"], ["Riya", "Sam", "Noor"])
        self.assertEqual(
            summary["decisions"],
            ["Add retry logging", "create a payment failure dashboard"],
        )
        self.assertEqual(
            summary["actions"],
            [
                {
                    "owner": "Sam",
                    "task": "Add structured logs",
                    "due_date": "2026-08-26",
                },
                {
                    "owner": "Noor",
                    "task": "Draft dashboard",
                    "due_date": "2026-08-28",
                },
            ],
        )

    def test_parse_notes_reports_missing_required_fields(self) -> None:
        incomplete = "Title: Standup\nAttendees: Riya\n"
        with self.assertRaises(MeetingNotesError) as ctx:
            parse_notes(incomplete)
        message = str(ctx.exception)
        self.assertIn("Owner", message)
        self.assertIn("Date", message)

    def test_action_must_have_exactly_three_values(self) -> None:
        notes = (
            "Title: Review\nOwner: Riya\nDate: 2026-08-24\n"
            "Actions: Sam|missing due date\n"
        )
        with self.assertRaises(MeetingNotesError) as ctx:
            parse_notes(notes)
        self.assertIn("exactly three", str(ctx.exception))


class FileHandlingTests(unittest.TestCase):
    def test_read_notes_missing_file_has_useful_message(self) -> None:
        missing = Path("/tmp/does-not-exist-meeting-notes.txt")
        with self.assertRaises(FileNotFoundError) as ctx:
            read_notes(missing)
        self.assertIn(str(missing), str(ctx.exception))
        self.assertIn("not found", str(ctx.exception).lower())

    def test_save_summary_creates_directory_and_indented_json(self) -> None:
        summary = parse_notes(SAMPLE_NOTES)
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "nested" / "meeting-summary.json"
            save_summary(summary, output_path)
            self.assertTrue(output_path.is_file())
            loaded = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["title"], "Checkout Reliability Review")
            # Indented JSON uses newlines rather than a single compact line.
            self.assertIn("\n  ", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
