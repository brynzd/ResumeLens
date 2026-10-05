"""Validate the structure of résumé specifications.

Demonstrates that textX accepts the specifications in ``examples/`` and
``tests/valid/`` and rejects those in ``tests/invalid/`` (missing mandatory
information, incorrect keywords, malformed structures, invalid nesting,
incorrect list syntax, incomplete candidate profiles).

Usage:
    python src/validator.py
"""

import sys

from textx.exceptions import TextXError

from parser import PROJECT_ROOT, get_metamodel

VALID_DIRS = [PROJECT_ROOT / "examples", PROJECT_ROOT / "tests" / "valid"]
INVALID_DIR = PROJECT_ROOT / "tests" / "invalid"


def validate_file(path, metamodel):
    """Return None if the file is valid, otherwise a description of the error."""
    try:
        metamodel.model_from_file(path)
    except TextXError as err:
        return f"{type(err).__name__} {err.line}:{err.col}: {err.message}"
    return None


def collect_cases():
    """Return (path, should_be_valid) pairs for every specification to check."""
    cases = [(path, True) for folder in VALID_DIRS for path in sorted(folder.glob("*.resume"))]
    cases += [(path, False) for path in sorted(INVALID_DIR.glob("*.resume"))]
    return cases


def main():
    metamodel = get_metamodel()
    cases = collect_cases()
    failures = 0

    for path, should_be_valid in cases:
        error = validate_file(path, metamodel)
        as_expected = (error is None) == should_be_valid
        if not as_expected:
            failures += 1

        mark = "ok  " if as_expected else "FAIL"
        verdict = "ACCEPTED" if error is None else "REJECTED"
        print(f"[{mark}] {verdict}  {path.relative_to(PROJECT_ROOT)}")
        if error:
            print(f"         {error}")

    print(f"\n{len(cases) - failures}/{len(cases)} specifications behaved as expected")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
