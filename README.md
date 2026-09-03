# Meeting Notes Parser

Python program that reads a meeting-notes text file, extracts title, owner, date, attendees, decisions, and action items, then writes them as indented JSON.

## Project layout

```
.
├── data/                      # sample input (assignment path)
│   └── meeting-notes.txt
├── output/                    # generated JSON (created on run)
│   └── meeting-summary.json
├── src/
│   └── learner_notes.py       # read_notes, parse_notes, save_summary
├── tests/
│   └── test_learner_notes.py
│   └── test_learner_notes_pytest.py
├── main.py                    # CLI entry point
└── README.md
```

This follows common Python conventions: lowercase folder names, `src/` for code, `tests/` for unit tests, `data/` for sample input, and `output/` for generated files.

There is no `utils/` folder. Shared helpers (`_split_list`, `_parse_actions`) live next to the parser in `src/learner_notes.py`. A utilities package is worth adding only when a second module needs the same helpers.

Run commands from the repository root so the default `data/` and `output/` paths resolve correctly.

## Requirements

- Python 3.9 or later
- pytest
  
## Input format

The program expects a text file with labeled lines. Example (`data/meeting-notes.txt`):

```
Title: Checkout Reliability Review
Owner: Riya
Date: 2026-08-24
Attendees: Riya, Sam, Noor
Decisions: Add retry logging; create a payment failure dashboard
Actions: Sam|Add structured logs|2026-08-26; Noor|Draft dashboard|2026-08-28
```

- **Attendees** are comma-separated.
- **Decisions** are semicolon-separated.
- **Actions** are semicolon-separated items. Each item must be `owner|task|due_date` (exactly three values).

`Title`, `Owner`, and `Date` are required. A missing input file or missing required field produces a clear error message.

## Setup

```bash
python --version
```

No virtual environment or `pip install` is needed.

## Run

Default paths (`data/meeting-notes.txt` → `output/meeting-summary.json`):

```bash
python main.py
```

Custom input path (and optional output path):

```bash
python main.py data/meeting-notes.txt
python main.py path/to/notes.txt -o output/meeting-summary.json
```

The `output/` directory is created automatically if it does not exist.

## Tests

```bash
python -m unittest discover -s tests -v
python -m pytest tests/test_learner_notes.py -v
```

## Program structure

- `read_notes(path)` — reads the file with `pathlib.Path`
- `parse_notes(text)` — returns a dictionary with lists for attendees, decisions, and actions
- `save_summary(summary, path)` — writes indented JSON and creates parent directories

## Reflection

Initially, developed this program in response to the earlier assignment and hence, developed at my free will. Later this assignment was created with automatic evaluation and hence, to follow the strict guidelines, lot of changes had to be done, for e.g. read_notes should NOT handle FileNotFound error, main.py should NOT be on the root. While mostly, I was able to cover the requirements, things like this Reflection, which I had missed out, was able to fix it ONLY after the failure. 
