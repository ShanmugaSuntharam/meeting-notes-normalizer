import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from meeting_notes import MeetingNotesError, parse_notes, read_notes, save_summary


SAMPLE_NOTES = """Title: Checkout Reliability Review
Owner: Riya
Date: 2026-08-24
Attendees: Riya, Sam, Noor
Decisions: Add retry logging; create a payment failure dashboard
Actions: Sam|Add structured logs|2026-08-26; Noor|Draft dashboard|2026-08-28
"""


def test_parse_notes_extracts_required_shape() -> None:
    summary = parse_notes(SAMPLE_NOTES)

    assert summary == {
        "title": "Checkout Reliability Review",
        "owner": "Riya",
        "date": "2026-08-24",
        "attendees": ["Riya", "Sam", "Noor"],
        "decisions": [
            "Add retry logging",
            "create a payment failure dashboard",
        ],
        "actions": [
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
    }


def test_parse_notes_reports_missing_required_fields() -> None:
    incomplete = "Title: Standup\nAttendees: Riya\n"

    with pytest.raises(MeetingNotesError) as context:
        parse_notes(incomplete)

    message = str(context.value)
    assert "Owner" in message
    assert "Date" in message


def test_action_must_have_exactly_three_values() -> None:
    notes = (
        "Title: Review\nOwner: Riya\nDate: 2026-08-24\n"
        "Actions: Sam|missing due date\n"
    )

    with pytest.raises(MeetingNotesError) as context:
        parse_notes(notes)

    assert "exactly three" in str(context.value)


def test_read_notes_missing_file_has_useful_message(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist-meeting-notes.txt"

    with pytest.raises(FileNotFoundError) as context:
        read_notes(missing)

    message = str(context.value)
    assert str(missing) in message
    assert "not found" in message.lower()


def test_save_summary_creates_directory_and_indented_json(tmp_path: Path) -> None:
    summary = parse_notes(SAMPLE_NOTES)
    output_path = tmp_path / "nested" / "meeting-summary.json"

    save_summary(summary, output_path)

    assert output_path.is_file()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["title"] == "Checkout Reliability Review"
    assert "\n  " in output_path.read_text(encoding="utf-8")
