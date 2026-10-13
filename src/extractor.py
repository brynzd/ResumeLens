"""Stage 1: extract the information of a plain-text résumé with regular expressions.

The strings are kept exactly as written. docs/regular_expressions.md explains
the language each pattern recognizes.
"""

import json
import re

# --- Personal information ---

# The name is the first non-empty line: two to five capitalized words,
# optionally joined by particles such as "de" or "van".
NAME_WORD = r"[A-ZÁÉÍÓÚÑÜ][A-Za-zÁÉÍÓÚÑÜáéíóúñü'’-]*"
NAME_PARTICLE = r"(?:de|del|la|las|los|van|von|da|di|y)"
NAME = re.compile(
    rf"\A\s*(?P<name>{NAME_WORD}(?:[ \t]+(?:{NAME_PARTICLE}[ \t]+)*{NAME_WORD}){{1,4}})[ \t]*$",
    re.MULTILINE,
)

# Lines "Headline: ...", "Location: ..." and "Summary: ..."
FIELD = re.compile(
    r"^[ \t]*(?P<key>headline|location|summary)[ \t]*:[ \t]*(?P<value>[^\n]*?)[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)

# --- Contact information ---

EMAIL = re.compile(r"[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")

# International numbers (+country code, optional area code and groups of
# digits) or ten-digit local numbers
PHONE = re.compile(
    r"(?<![\w+])(?:\+\d{1,3}(?:[ -]?\(\d{1,4}\))?(?:[ -]?\d{1,4}){2,4}"
    r"|\d{3}[ -]?\d{3}[ -]?\d{4})(?!\d)"
)

LINKEDIN = re.compile(r"https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?")

# --- Skills: one pattern per category ---

PROGRAMMING_LANGUAGES = r"java[ \t]?script|type[ \t]?script|python3?|scala|css3?|(?<!\.)js|(?<!\.)ts"
FRAMEWORKS_LIBRARIES = (
    r"react(?:[ \t.]?js)?|angular(?:[ \t.]?js)?|vue(?:[ \t.]?js)?"
    r"|node(?:[ \t.]?js)?|django|spring[ \t-]?boot|tailwind(?:[ \t]?css)?"
    r"|pandas|num[ \t]?py|sklearn|scikit[ \t-]?learn|tensor[ \t]?flow|py[ \t]?torch"
)
DATABASES = r"postgres(?:ql)?|mongo(?:[ \t]?db)?|sql"
TOOLS = (
    r"git|(?:apache[ \t])?spark|pyspark|(?:apache[ \t])?airflow"
    r"|docker|kubernetes|aws|gcp|terraform"
)

# Union of the four categories, with a named group for each one. The text is
# scanned once from left to right, so "Node.js" is read as a framework and its
# "js" is not read again as a language.
SKILLS = re.compile(
    rf"\b(?:(?P<programming_languages>{PROGRAMMING_LANGUAGES})"
    rf"|(?P<frameworks_libraries>{FRAMEWORKS_LIBRARIES})"
    rf"|(?P<databases>{DATABASES})"
    rf"|(?P<tools>{TOOLS}))\b",
    re.IGNORECASE,
)
SKILL_CATEGORIES = ["programming_languages", "frameworks_libraries", "databases", "tools"]

# The list after "Skills:" or "Technical Skills:", on the same line or the next one
SKILLS_LIST = re.compile(
    r"^[ \t]*(?:technical[ \t]+)?skills[ \t]*:[ \t]*\n?[ \t]*(?P<items>[^\n]+)",
    re.MULTILINE | re.IGNORECASE,
)
LIST_SEPARATOR = re.compile(r"[ \t]*[,;][ \t]*")

# Qualifications that are phrases, not tools
OTHER_QUALIFICATIONS = re.compile(
    r"\b(?:rest(?:ful)?[ \t]+apis?|(?:predictive|machine[ \t-]learning)[ \t]+models?"
    r"|data[ \t-]processing[ \t]+pipelines?|web[ \t]+applications?)\b",
    re.IGNORECASE,
)

# --- Academic qualifications and professional experience ---

ACADEMIC = re.compile(
    r"\b(?:B\.?[ \t]?Sc\.?|M\.?[ \t]?Sc\.?|Ph\.?[ \t]?D\.?|Bachelor(?:'s)?|Master(?:'s)?"
    r"|Specialization|Diploma|Systems Engineering|Computer Science|Engineering|Ingenier[íi]a)"
    r"(?![A-Za-z])",
    re.IGNORECASE,
)

YEARS = re.compile(
    r"\b(?P<years>\d{1,2})\+?[ \t]+(?:years?|años?|anos?)[ \t]+"
    r"(?:of|de)[ \t]+(?:experience|experiencia)\b",
    re.IGNORECASE,
)

# Section headers on a line of their own: "Experience:", "Education:", ...
SECTION = re.compile(
    r"^[ \t]*(?P<section>technical skills|skills|languages|experience|education)[ \t]*:[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)

# YYYY-MM or YYYY-MM-DD, the same language as the DATE terminal of the DSL
DATE = r"\d{4}-(?:0[1-9]|1[0-2])(?:-(?:0[1-9]|[12]\d|3[01]))?"

# "Title at Organization (start - end)", for positions and degrees
ENTRY = re.compile(
    rf"^[ \t]*(?P<title>[^\n]+?)[ \t]+at[ \t]+(?P<organization>[^\n(]+?)[ \t]*"
    rf"\((?P<start>{DATE})[ \t]*[-–][ \t]*(?P<end>{DATE}|present)\)[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)

# "- task" lines below a position
TASK = re.compile(r"^[ \t]*[-•*][ \t]+(?P<task>[^\n]+?)[ \t]*$", re.MULTILINE)

# "English: native", "Spanish (full professional)", "French - basic"
LANGUAGE = re.compile(
    r"^[ \t]*(?P<name>[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)[ \t]*(?::|-|–|\()[ \t]*"
    r"(?P<level>native|full[ _]professional|professional|basic)\)?[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)


def unique(items):
    """The items without repetitions, in order of first appearance."""
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def first_match(pattern, text):
    """The first string of the text that the pattern recognizes, or None."""
    match = pattern.search(text)
    if match is None:
        return None
    return match.group()


def split_sections(text):
    """Text of every headed section: {"experience": "...", "education": "...", ...}."""
    # With a group in the pattern, split returns [before, name, text, name, text, ...]
    parts = SECTION.split(text)
    sections = {}
    for i in range(1, len(parts), 2):
        sections[parts[i].lower()] = parts[i + 1]
    return sections


def extract_entries(section, with_tasks):
    """Entries "Title at Organization (start - end)" of a section."""
    matches = list(ENTRY.finditer(section))
    entries = []
    for i, match in enumerate(matches):
        entry = {
            "title": match["title"],
            "organization": match["organization"],
            "start": match["start"],
            "end": match["end"].lower(),
        }
        if with_tasks:
            # The tasks are the "- ..." lines up to the next entry
            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(section)
            lines = section[match.end():end]
            entry["tasks"] = [task["task"] for task in TASK.finditer(lines)]
        entries.append(entry)
    return entries


def extract_languages(section):
    """Spoken languages with their level, written as the keyword of the DSL."""
    languages = []
    for match in LANGUAGE.finditer(section):
        level = match["level"].lower().replace(" ", "_")
        languages.append({"name": match["name"], "level": level})
    return languages


def unrecognized_skills(text):
    """Items of the skills list that are not a known skill, such as "COBOL"."""
    skills_list = SKILLS_LIST.search(text)
    if skills_list is None:
        return []
    items = LIST_SEPARATOR.split(skills_list["items"].strip().rstrip("."))
    return [item for item in items if item and not SKILLS.fullmatch(item)]


def extract_resume_entities(text):
    """Extract every type of information of a résumé, grouped in a dictionary."""
    name = NAME.search(text)
    years = YEARS.search(text)
    sections = split_sections(text)

    fields = {}
    for match in FIELD.finditer(text):
        key = match["key"].lower()
        if key not in fields:
            fields[key] = match["value"] or None

    found = {category: [] for category in SKILL_CATEGORIES}
    technologies = []
    for match in SKILLS.finditer(text):
        found[match.lastgroup].append(match.group())  # lastgroup: the category matched
        technologies.append(match.group())

    skills = {}
    for category in SKILL_CATEGORIES:
        skills[category] = unique(found[category])
    skills["unrecognized"] = unique(unrecognized_skills(text))

    return {
        "personal": {
            "name": name["name"] if name else None,
            "headline": fields.get("headline"),
            "location": fields.get("location"),
            "summary": fields.get("summary"),
        },
        "contact": {
            "email": first_match(EMAIL, text),
            "phone": first_match(PHONE, text),
            "linkedin": first_match(LINKEDIN, text),
        },
        "skills": skills,
        # Input of stage 2: every skill string, then the unknown items of the list
        "technologies": unique(technologies + skills["unrecognized"]),
        "other_qualifications": unique(OTHER_QUALIFICATIONS.findall(text)),
        "academic_qualifications": unique(ACADEMIC.findall(text)),
        "experience_years": int(years["years"]) if years else None,
        "experience": extract_entries(sections.get("experience", ""), with_tasks=True),
        "education": extract_entries(sections.get("education", ""), with_tasks=False),
        "languages": extract_languages(sections.get("languages", "")),
    }


def save_extracted_data(data, path):
    """Store the extracted information in a JSON file."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
