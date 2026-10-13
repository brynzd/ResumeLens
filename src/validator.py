"""Validate résumé specifications written in the ResumeLens DSL.

Validation happens at three levels:

- Lexical: every token must match its terminal (EMAIL, DATE, CANON, ...).
- Syntactic: the tokens must follow the context-free grammar in
  ``grammar/resume.tx``.
- Semantic: rules the grammar cannot express, checked on the parsed model
  (non-empty name, headline and location; at least one contact method;
  periods that do not end before they start; unique, canonical skills;
  a consistent classification whose verdicts are the ones the stage-3
  profile automata give for the listed skills).

textX enforces the first two levels while parsing (``TextXSyntaxError``). The
semantic rules are object processors registered on the metamodel
(``TextXSemanticError``).

Running the module demonstrates that the specifications in ``examples/`` and
``tests/valid/`` are accepted and that those in ``tests/invalid/`` are
rejected (missing mandatory information, incorrect keywords, malformed
structures, invalid nesting, incorrect list syntax, incomplete candidate
profiles, lexical and semantic errors).

Usage:
    python src/validator.py
"""

import sys

from textx import TextXSemanticError, get_location
from textx.exceptions import TextXError

from classifier import classify
from parser import PROJECT_ROOT, get_metamodel

VALID_DIRS = [PROJECT_ROOT / "examples", PROJECT_ROOT / "tests" / "valid"]
INVALID_DIR = PROJECT_ROOT / "tests" / "invalid"

# Output alphabet (Gamma) of the stage-2 transducers, as listed in
# docs/domain.md: the only skills a candidate profile may contain.
CANONICAL_SKILLS = {
    "JAVASCRIPT", "TYPESCRIPT", "PYTHON", "SCALA",
    "REACT", "ANGULAR", "VUE",
    "CSS", "TAILWIND",
    "NODE_JS", "DJANGO", "SPRING_BOOT",
    "PANDAS", "NUMPY",
    "SCIKIT_LEARN", "TENSORFLOW", "PYTORCH",
    "SPARK", "AIRFLOW",
    "POSTGRESQL", "MONGODB", "SQL",
    "GIT",
}


def semantic_error(message, obj):
    """Reject the model with an error located at ``obj`` (line and column)."""
    raise TextXSemanticError(message, **get_location(obj))


def check_candidate(candidate):
    if not candidate.name.strip():
        semantic_error("candidate name cannot be empty", candidate)
    # textX runs the processor of the root last, after the checks of its
    # sections, so the skills are already known to be canonical and unique.
    check_verdicts(candidate)


def check_verdicts(candidate):
    # Each verdict must be the one the profile's DFA gives for the listed
    # skills, and UNQUALIFIED is ACCEPTED exactly when no profile is.
    accepted = classify(list(candidate.skills.items))
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
    for field in ("headline", "location"):
        if not getattr(header, field).strip():
            semantic_error(f"{field} cannot be empty", header)


def check_contact(contact):
    if not (contact.email or contact.phone or contact.linkedin):
        semantic_error("contact needs at least one of: email, phone, linkedin", contact)


def check_skills(skills):
    seen = set()
    for skill in skills.items:
        if skill not in CANONICAL_SKILLS:
            semantic_error(f"'{skill}' is not a canonical skill", skills)
        if skill in seen:
            semantic_error(f"duplicate skill '{skill}'", skills)
        seen.add(skill)


def check_period(period):
    # Dates are fixed-width 'YYYY-MM[-DD]' strings, so comparing their
    # 'YYYY-MM' prefixes as text is the same as comparing them in time.
    if period.end != "present" and period.end[:7] < period.start[:7]:
        semantic_error(f"period ends ({period.end}) before it starts ({period.start})", period)


def check_classification(classification):
    profiles = [result.profile for result in classification.items]
    for profile in profiles:
        if profiles.count(profile) > 1:
            semantic_error(f"profile '{profile}' is classified more than once", classification)

    accepted = [result.profile for result in classification.items if result.verdict == "ACCEPTED"]
    if "UNQUALIFIED" in accepted and len(accepted) > 1:
        semantic_error("UNQUALIFIED cannot be ACCEPTED together with another profile", classification)


# Grammar rule -> function textX calls on every object built from that rule.
SEMANTIC_CHECKS = {
    "CandidateProfile": check_candidate,
    "Header": check_header,
    "Contact": check_contact,
    "Skills": check_skills,
    "Period": check_period,
    "Classification": check_classification,
}


def get_validating_metamodel():
    """Return the metamodel with the semantic checks registered."""
    metamodel = get_metamodel()
    metamodel.register_obj_processors(SEMANTIC_CHECKS)
    return metamodel


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
