"""Extract structured fields from a meeting-notes text file and save JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

#Mandatory fields that must be present in the meeting notes. If any of these fields are missing, 
# a MeetingNotesError will be raised. The field names are case-insensitive and can have leading or 
# trailing whitespace.
REQUIRED_FIELDS = ("Title", "Owner", "Date")

#The below dictionary is used to map the field names in the meeting notes 
# to the keys we want to use in our structured output. This allows us to handle 
# variations in capitalization and spacing in the input text or even to map
# both "subject" and "title" to "title"
#This is definitely useful if more than 1 alias is used for a field, we can 
# add it to the dictionary and map it to the same key. For example, if we want 
# to allow "Meeting Title" as an alias for "Title", we can add "meeting title": "title" to the dictionary.
#Otherwise, having these aliases in a SET is sufficient, but we would have to check for each alias 
# separately in the code, which is less efficient and more error-prone.
FIELD_ALIASES = {
    "title": "title",
    "owner": "owner",
    "date": "date",
    "attendees": "attendees",
    "decisions": "decisions",
    "actions": "actions",
}


class MeetingNotesError(ValueError):
    """Raised when meeting notes are missing required fields or malformed."""


def read_notes(path: Path) -> str:
    """Read meeting notes from *path* using pathlib."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Meeting notes file not found: {path}\n"
            "Provide a path to an existing text file, for example: "
            "python3 src/main.py data/meeting-notes.txt"
        )
    return path.read_text(encoding="utf-8")


def _split_list(value: str, delimiter: str) -> list[str]:
    parts = [item.strip() for item in value.split(delimiter)]

    #useful, when we have a empty string, between 2 delmiter there is nothing
    return [item for item in parts if item] 


def _parse_actions(raw: str) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []

    #if the raw string is empty or contains only whitespace, return an empty list of actions
    if not raw.strip():
        return actions

    for item in _split_list(raw, ";"):
        parts = [part.strip() for part in item.split("|")]

        #if there are more than 3 parts or if any of the parts are empty, raise a 
        # MeetingNotesError with a message indicating that each action must have exactly three '|' -separated values (owner|task|due_date) and include the invalid action in the message.
        if len(parts) != 3 or not all(parts):
            raise MeetingNotesError(
                "Each action must have exactly three '|' -separated values "
                f"(owner|task|due_date). Invalid action: {item!r}"
            )
        owner, task, due_date = parts
        actions.append({"owner": owner, "task": task, "due_date": due_date})
    return actions


def parse_notes(text: str) -> dict[str, Any]:
    """Parse meeting-notes text into a dictionary of structured fields."""
    fields: dict[str, str] = {}
    for line in text.splitlines():

        #Removing leading and trailing whitespace from the line, so that we can process it easily
        stripped = line.strip()

        #empty string is considered False in Python, if the line is empty or 
        #if there is NO collon in the line, then skip the line processing
        if not stripped or ":" not in stripped:
            continue

        #if position 1 is NOT given, if there are more than 1 collons
        #split returns multiple values and hence, the assignment will fail
        label, value = stripped.split(":", 1)

        #What if there is a case mismatch in the label, we can use lower() to convert it to lower case and then check if it is in the FIELD_ALIASES dictionary
        key = label.strip().lower()
        if key in FIELD_ALIASES:
            fields[FIELD_ALIASES[key]] = value.strip()

    #if any of the 3 mandatory fields are missing, raise a MeetingNotesError with a message indicating 
    # which fields are missing and what the expected format is. The message should include the names of 
    # the missing fields and an example of the expected lines in the meeting notes.
    missing = [name for name in REQUIRED_FIELDS if name.lower() not in fields or not fields[name.lower()]]
    if missing:
        raise MeetingNotesError(
            "Meeting notes are missing required field(s): "
            + ", ".join(missing)
            + ". Expected lines like 'Title: ...', 'Owner: ...', and 'Date: ...'."
        )

    attendees = _split_list(fields.get("attendees", ""), ",")
    decisions = _split_list(fields.get("decisions", ""), ";")
    actions = _parse_actions(fields.get("actions", ""))

    return {
        "title": fields["title"],
        "owner": fields["owner"],
        "date": fields["date"],
        "attendees": attendees,
        "decisions": decisions,
        "actions": actions,
    }


def save_summary(summary: dict[str, Any], path: Path) -> None:
    """Write *summary* as indented JSON, creating the output directory if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
