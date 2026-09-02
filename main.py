#!/usr/bin/env python3
"""CLI entry point: parse meeting notes and write a JSON summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.learner_notes import MeetingNotesError, parse_notes, read_notes, save_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Parse meeting notes into structured JSON.",
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        default="data/meeting-notes.txt",
        type=Path,
        help="Path to the meeting-notes text file (default: data/meeting-notes.txt)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output/meeting-summary.json",
        type=Path,
        help="Path for the JSON summary (default: output/meeting-summary.json)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        text = read_notes(args.input_path)
        summary = parse_notes(text)
        save_summary(summary, args.output)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1
    except MeetingNotesError as exc:
        print(f"Invalid meeting notes: {exc}", file=sys.stderr)
        return 1

    print(f"Created: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
