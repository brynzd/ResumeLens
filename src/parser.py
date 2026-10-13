"""Parse a .resume file with the textX grammar of the candidate profile DSL.

Usage:
    python src/parser.py examples/resume_01.resume
"""

import sys
from pathlib import Path

from textx import metamodel_from_file
from textx.exceptions import TextXSyntaxError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAMMAR_PATH = PROJECT_ROOT / "grammar" / "resume.tx"


def get_metamodel():
    """Metamodel of grammar/resume.tx: it checks the lexical and syntactic rules."""
    return metamodel_from_file(GRAMMAR_PATH)


def parse_file(path, metamodel):
    """Model (CandidateProfile) of a .resume file."""
    return metamodel.model_from_file(path)


def main():
    if len(sys.argv) != 2:
        print("Usage: python src/parser.py <file.resume>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        candidate = parse_file(path, get_metamodel())
    except FileNotFoundError:
        print(f"error: file not found: {path}")
        sys.exit(1)
    except TextXSyntaxError as err:
        print(f"{path}:{err.line}:{err.col}: syntax error: {err.message}")
        sys.exit(1)

    print(f"OK: {path} conforms to the ResumeLens grammar.")
    print("candidate:  ", candidate.name)
    print("skills:     ", ", ".join(candidate.skills.items))
    print("experiences:", len(candidate.experiences.items))
    print("degrees:    ", len(candidate.education.items))
    for result in candidate.classification.items:
        print(f"  {result.profile} -> {result.verdict}")


if __name__ == "__main__":
    main()
