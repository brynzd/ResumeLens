"""Validate .resume files at three levels: lexical, syntactic and semantic.

textX checks the lexical and syntactic rules of grammar/resume.tx while it
parses. The semantic rules are functions that textX calls on the objects of
the parsed model (object processors).

Run as a script, it checks that every file of examples/ and tests/valid/ is
accepted and that every file of tests/invalid/ is rejected.

Usage:
    python src/validator.py
"""

import sys

from textx import TextXSemanticError, get_location
from textx.exceptions import TextXError

from classifier import classify
from normalizer import GLOBAL_ORDER
from parser import PROJECT_ROOT, get_metamodel

VALID_DIRS = [PROJECT_ROOT / "examples", PROJECT_ROOT / "tests" / "valid"]
INVALID_DIR = PROJECT_ROOT / "tests" / "invalid"


def semantic_error(message, obj):
    """Reject the document with an error at the line and column of obj."""
    raise TextXSemanticError(message, **get_location(obj))


def check_candidate(candidate):
    if not candidate.name.strip():
        semantic_error("candidate name cannot be empty", candidate)
    # textX checks the root last, so the skills are already canonical and unique
    check_verdicts(candidate)


def check_verdicts(candidate):
    """Every verdict must be the one the profile automaton gives for the skills."""
    accepted = classify(candidate.skills.items)
    for result in candidate.classification.items:
        if result.profile == "UNQUALIFIED":
            expected = "REJECTED" if any(accepted.values()) else "ACCEPTED"
        else:
            expected = "ACCEPTED" if accepted[result.profile] else "REJECTED"
        if result.verdict != expected:
            semantic_error(
                f"{result.profile} -> {result.verdict} contradicts the profile automaton,"
                f" which gives {expected} for these skills",
                result,
            )


def check_header(header):
    if not header.headline.strip():
        semantic_error("headline cannot be empty", header)
    if not header.location.strip():
        semantic_error("location cannot be empty", header)


def check_contact(contact):
    if not (contact.email or contact.phone or contact.linkedin):
        semantic_error("contact needs at least one of: email, phone, linkedin", contact)


def check_skills(skills):
    seen = []
    for skill in skills.items:
        if skill not in GLOBAL_ORDER:
            semantic_error(f"'{skill}' is not a canonical skill", skills)
        if skill in seen:
            semantic_error(f"duplicate skill '{skill}'", skills)
        seen.append(skill)


def check_period(period):
    # Compare year and month: YYYY-MM strings sort in the same order as the dates
    if period.end != "present" and period.end[:7] < period.start[:7]:
        semantic_error(f"period ends ({period.end}) before it starts ({period.start})", period)


def check_classification(classification):
    seen = []
    for result in classification.items:
        if result.profile in seen:
            message = f"profile '{result.profile}' is classified more than once"
            semantic_error(message, classification)
        seen.append(result.profile)


# Grammar rule -> function textX calls on every object of that rule
SEMANTIC_CHECKS = {
    "CandidateProfile": check_candidate,
    "Header": check_header,
    "Contact": check_contact,
    "Skills": check_skills,
    "Period": check_period,
    "Classification": check_classification,
}


def get_validating_metamodel():
    """Metamodel of the grammar with the semantic checks registered."""
    metamodel = get_metamodel()
    metamodel.register_obj_processors(SEMANTIC_CHECKS)
    return metamodel


def validate_file(path, metamodel):
    """None if the file is valid, otherwise a description of the error."""
    try:
        metamodel.model_from_file(path)
    except TextXError as err:
        return f"{type(err).__name__} {err.line}:{err.col}: {err.message}"
    return None


def collect_cases():
    """Pairs (path, should be valid) for every specification to check."""
    cases = []
    for folder in VALID_DIRS:
        for path in sorted(folder.glob("*.resume")):
            cases.append((path, True))
    for path in sorted(INVALID_DIR.glob("*.resume")):
        cases.append((path, False))
    return cases


def main():
    metamodel = get_validating_metamodel()
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
