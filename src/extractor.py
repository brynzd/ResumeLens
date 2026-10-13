"""Stage 1 - extract candidate information from a plain-text résumé.

Every type of information has its own regular expression, implemented with
Python's ``re`` module; docs/regular_expressions.md explains the language
each one recognizes. Extraction only finds strings: it keeps them exactly
as written (FR-08) and does not decide whether two strings are equivalent
(stage 2) or whether the candidate satisfies a profile (stage 3).

The result is a dictionary grouped by type of information (FR-09), which
``save_extracted_data`` stores as JSON.

Usage:
    python src/extractor.py data/resumes/wednesday.txt
"""

import json
import os
import re
import sys

# --- Personal information -------------------------------------------------

# A name is the first non-empty line of the résumé: two to five words that
# start with a capital letter (accents, apostrophes and hyphens allowed),
# optionally joined by lowercase particles such as "de" or "van".
NAME_WORD = r"[A-ZÁÉÍÓÚÑÜ][A-Za-zÁÉÍÓÚÑÜáéíóúñü'’-]*"
NAME_PARTICLE = r"(?:de|del|la|las|los|van|von|da|di|y)"
NAME = re.compile(
    rf"\A\s*(?P<name>{NAME_WORD}(?:[ \t]+(?:{NAME_PARTICLE}[ \t]+)*{NAME_WORD}){{1,4}})[ \t]*$",
    re.MULTILINE,
)

# "Headline: ...", "Location: ...", "Summary: ..." lines.
FIELD = re.compile(
    r"^[ \t]*(?P<key>headline|location|summary)[ \t]*:[ \t]*(?P<value>[^\n]*?)[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)

# --- Contact information --------------------------------------------------

EMAIL = re.compile(r"[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")

# International numbers (+country code, an optional area code in
# parentheses and two to four groups of digits) or ten-digit local numbers.
# The groups are non-capturing on purpose: re.findall returns the captured
# groups instead of the whole match when a pattern has any.
PHONE = re.compile(
    r"(?<![\w+])(?:\+\d{1,3}(?:[ -]?\(\d{1,4}\))?(?:[ -]?\d{1,4}){2,4}"
    r"|\d{3}[ -]?\d{3}[ -]?\d{4})(?!\d)"
)

LINKEDIN = re.compile(r"https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?")

# --- Skills: programming languages, frameworks, databases, tools ----------

# One pattern per category. They are combined into a single pattern with
# named groups, so finditer scans the text once, left to right, without
# overlapping matches: "Node.js" is read as a framework before its "js"
# could be read as a language. "js"/"ts" right after a dot ("Next.js",
# "app.ts") are file extensions, not the languages.
SKILL_PATTERNS = {
    "programming_languages": (
        r"java[ \t]?script|type[ \t]?script|python3?|scala|css3?|(?<!\.)js|(?<!\.)ts"
    ),
    "frameworks_libraries": (
        r"react(?:[ \t.]?js)?|angular(?:[ \t.]?js)?|vue(?:[ \t.]?js)?"
        r"|node(?:[ \t.]?js)?|django|spring[ \t-]?boot|tailwind(?:[ \t]?css)?"
        r"|pandas|num[ \t]?py|sklearn|scikit[ \t-]?learn|tensor[ \t]?flow|py[ \t]?torch"
    ),
    "databases": r"postgres(?:ql)?|mongo(?:[ \t]?db)?|sql",
    "tools": (
        r"git|(?:apache[ \t])?spark|pyspark|(?:apache[ \t])?airflow"
        r"|docker|kubernetes|aws|gcp|terraform"
    ),
}
SKILLS = re.compile(
    r"\b(?:" + "|".join(f"(?P<{cat}>{pattern})" for cat, pattern in SKILL_PATTERNS.items()) + r")\b",
    re.IGNORECASE,
)

# The list after "Skills:" or "Technical Skills:", on the same line or the
# next one. Its items that no skill pattern recognizes ("COBOL") are kept as
# unrecognized, so stage 2 can report them instead of losing them silently.
SKILLS_LIST = re.compile(
    r"^[ \t]*(?:technical[ \t]+)?skills[ \t]*:[ \t]*\n?[ \t]*(?P<items>[^\n]+)",
    re.MULTILINE | re.IGNORECASE,
)
LIST_SEPARATOR = re.compile(r"[ \t]*[,;][ \t]*")

# Descriptive phrases that are qualifications but not tools (FR-07).
OTHER_QUALIFICATIONS = re.compile(
    r"\b(?:rest(?:ful)?[ \t]+apis?|(?:predictive|machine[ \t-]learning)[ \t]+models?"
    r"|data[ \t-]processing[ \t]+pipelines?|web[ \t]+applications?)\b",
    re.IGNORECASE,
)

# --- Academic qualifications and professional experience ------------------

ACADEMIC = re.compile(
    r"\b(?:B\.?[ \t]?Sc\.?|M\.?[ \t]?Sc\.?|Ph\.?[ \t]?D\.?|Bachelor(?:'s)?|Master(?:'s)?"
    r"|Specialization|Diploma|Systems Engineering|Computer Science|Engineering|Ingenier[íi]a)"
    r"(?![A-Za-z])",
    re.IGNORECASE,
)

YEARS = re.compile(
    r"\b(?P<years>\d{1,2})\+?[ \t]+(?:years?|años?|anos?)[ \t]+(?:of|de)[ \t]+(?:experience|experiencia)\b",
    re.IGNORECASE,
)

# Section headers on a line of their own: "Experience:", "Education:", ...
SECTION = re.compile(
    r"^[ \t]*(?P<section>technical skills|skills|languages|experience|education)[ \t]*:[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)

# Same language as the DATE terminal of the DSL: YYYY-MM or YYYY-MM-DD.
DATE = r"\d{4}-(?:0[1-9]|1[0-2])(?:-(?:0[1-9]|[12]\d|3[01]))?"

# "Title at Organization (start - end)", used for positions and degrees.
ENTRY = re.compile(
    rf"^[ \t]*(?P<title>[^\n]+?)[ \t]+at[ \t]+(?P<organization>[^\n(]+?)[ \t]*"
    rf"\((?P<start>{DATE})[ \t]*[-–][ \t]*(?P<end>{DATE}|present)\)[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)

# "- task" lines below a position.
TASK = re.compile(r"^[ \t]*[-•*][ \t]+(?P<task>[^\n]+?)[ \t]*$", re.MULTILINE)

# "English: native", "Spanish (full professional)", "French - basic".
LANGUAGE = re.compile(
    r"^[ \t]*(?P<name>[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)[ \t]*(?::|-|–|\()[ \t]*"
    r"(?P<level>native|full[ _]professional|professional|basic)\)?[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)


def unique(items):
    """Keep the first occurrence of every item, in order."""
    return list(dict.fromkeys(items))


def unrecognized_skills(text):
    """Items of the skills list that are not, as a whole, a known skill."""
    listed = SKILLS_LIST.search(text)
    if not listed:
        return []
    items = LIST_SEPARATOR.split(listed["items"].strip().rstrip("."))
    return [item for item in items if item and not SKILLS.fullmatch(item)]


def split_sections(text):
    """Return {'experience': text, 'education': text, ...} for the headed sections."""
    parts = SECTION.split(text)
    return {parts[i].lower(): parts[i + 1] for i in range(1, len(parts), 2)}


def extract_entries(block, with_tasks):
    """Entries 'Title at Organization (start - end)' of a section."""
    matches = list(ENTRY.finditer(block))
    entries = []
    for i, match in enumerate(matches):
        entry = {
            "title": match["title"],
            "organization": match["organization"],
            "start": match["start"],
            "end": match["end"].lower(),
        }
        if with_tasks:
            end = matches[i + 1].start() if i + 1 < len(matches) else len(block)
            entry["tasks"] = [t["task"] for t in TASK.finditer(block, match.end(), end)]
        entries.append(entry)
    return entries


def extract_resume_entities(text_content: str) -> dict:
    """Extract every type of information from a plaintext résumé."""
    sections = split_sections(text_content)
    name = NAME.search(text_content)
    fields = {}
    for match in FIELD.finditer(text_content):
        fields.setdefault(match["key"].lower(), match["value"] or None)
    years = YEARS.search(text_content)

    skills = {category: [] for category in SKILL_PATTERNS}
    for match in SKILLS.finditer(text_content):
        skills[match.lastgroup].append(match.group())
    skills["unrecognized"] = unrecognized_skills(text_content)

    def first(pattern):
        found = pattern.search(text_content)
        return found.group() if found else None

    return {
        "personal": {
            "name": name["name"] if name else None,
            "headline": fields.get("headline"),
            "location": fields.get("location"),
            "summary": fields.get("summary"),
        },
        "contact": {
            "email": first(EMAIL),
            "phone": first(PHONE),
            "linkedin": first(LINKEDIN),
        },
        "skills": {category: unique(found) for category, found in skills.items()},
        # Every skill string in order of appearance, then the unrecognized
        # items of the skills list: the input of stage 2.
        "technologies": unique(
            [m.group() for m in SKILLS.finditer(text_content)] + skills["unrecognized"]
        ),
        "other_qualifications": unique(m.group() for m in OTHER_QUALIFICATIONS.finditer(text_content)),
        "academic_qualifications": unique(m.group() for m in ACADEMIC.finditer(text_content)),
        "experience_years": int(years["years"]) if years else None,
        "experience": extract_entries(sections.get("experience", ""), with_tasks=True),
        "education": extract_entries(sections.get("education", ""), with_tasks=False),
        "languages": [
            {"name": m["name"], "level": m["level"].lower().replace(" ", "_")}
            for m in LANGUAGE.finditer(sections.get("languages", ""))
        ],
    }


def save_extracted_data(extracted_data: dict, output_path: str = "extracted_resume.json"):
    """
    Saves the structured extracted data into a persistent file (JSON format),
    ensuring that the parent directory exists beforehand.
    """
    # Get the directory path from output_path (if any)
    directory = os.path.dirname(output_path)
    if directory:
        # Create the directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/extractor.py <resume.txt>")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as file:
        print(json.dumps(extract_resume_entities(file.read()), indent=4, ensure_ascii=False))
