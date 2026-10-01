"""Parse résumé specifications written in the ResumeLens DSL.

Loads the textX metamodel from ``grammar/resume.tx`` and builds the model of a
``.resume`` file, reporting the error when the file does not conform to the
grammar.

Usage:
    python src/parser.py examples/resume_01.resume
"""

import sys
from pathlib import Path

from textx import metamodel_from_file
from textx.exceptions import TextXSyntaxError

# Folder of the project (one level above src/), so the script works
# no matter where you run it from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAMMAR_PATH = PROJECT_ROOT / "grammar" / "resume.tx"


def get_metamodel():
    """Load the grammar and return the textX metamodel."""
    return metamodel_from_file(GRAMMAR_PATH)


def parse_file(path, metamodel):
    """Parse a .resume file and return its model (a CandidateProfile)."""
    return metamodel.model_from_file(path)


def main():
    if len(sys.argv) != 2:
        print("Usage: python src/parser.py <file.resume>")
        sys.exit(1)

    path = sys.argv[1]
    metamodel = get_metamodel()

    try:
        candidate = parse_file(path, metamodel)
    except FileNotFoundError:
        print(f"error: file not found: {path}")
        sys.exit(1)
    except TextXSyntaxError as err:
        print(f"{path}:{err.line}:{err.col}: syntax error: {err.message}")
        sys.exit(1)

    # If we got here the file is valid: show what was parsed.
    print(f"OK: {path} conforms to the ResumeLens grammar.")
    print("candidate:  ", candidate.name)
    print("skills:     ", ", ".join(candidate.skills.items))
    print("experiences:", len(candidate.experiences.items))
    print("degrees:    ", len(candidate.education.items))
    for result in candidate.classification.items:
        print(f"  {result.profile} -> {result.verdict}")


if __name__ == "__main__":
    main()
