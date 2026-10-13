"""Write the candidate profile document (.resume) from the pipeline results (FR-18).

The document follows grammar/resume.tx with the information of the three
previous stages: what stage 1 extracted, the canonical skills of stage 2
in the global canonical order, and the verdict of every profile from
stage 3 (plus UNQUALIFIED -> ACCEPTED when no profile accepts).

Nothing is invented. When the résumé lacks a mandatory part (a headline,
the contact information, an experience, ...) it is written empty, and
textX rejects the document as an incomplete candidate profile.
"""

from normalizer import GLOBAL_ORDER
from profiles import PROFILES

INDENT = "    "


def quote(text):
    """Write a DSL STRING: double quotes and backslashes in the text are replaced."""
    return '"' + (text or "").replace("\\", "/").replace('"', "'") + '"'


def missing_information(data, tokens):
    """Mandatory parts of a candidate document the résumé does not provide."""
    personal = data["personal"]
    present = {
        "name": personal["name"],
        "headline": personal["headline"],
        "location": personal["location"],
        "contact (email, phone or linkedin)": any(data["contact"].values()),
        "skills": tokens,
        "experience": data["experience"],
        "education": data["education"],
    }
    return [part for part, value in present.items() if not value]


def build_resume(data, tokens, verdicts):
    """Return the text of the candidate profile document."""
    personal, contact = data["personal"], data["contact"]
    lines = [
        f"candidate {quote(personal['name'])} {{",
        f"{INDENT}headline: {quote(personal['headline'])};",
        f"{INDENT}location: {quote(personal['location'])};",
    ]
    if personal["summary"]:
        lines.append(f"{INDENT}summary: {quote(personal['summary'])};")

    lines += ["", f"{INDENT}contact {{"]
    lines += [f"{INDENT * 2}{key}: {contact[key]};" for key in ("email", "phone", "linkedin") if contact[key]]
    lines.append(f"{INDENT}}}")

    skills = ", ".join(sorted(tokens, key=GLOBAL_ORDER.index))
    lines += ["", f"{INDENT}skills {{", f"{INDENT * 2}{skills}", f"{INDENT}}}"]

    if data["languages"]:
        lines += ["", f"{INDENT}languages {{"]
        lines += [f"{INDENT * 2}{quote(lang['name'])}: {lang['level']};" for lang in data["languages"]]
        lines.append(f"{INDENT}}}")

    lines += ["", f"{INDENT}experience {{"]
    for job in data["experience"]:
        header = (
            f"{INDENT * 2}role {quote(job['title'])} at {quote(job['organization'])}"
            f" from {job['start']} to {job['end']}"
        )
        if job["tasks"]:
            lines.append(header + " {")
            lines += [f"{INDENT * 3}- {quote(task)}" for task in job["tasks"]]
            lines.append(f"{INDENT * 2}}}")
        else:
            lines.append(header)
    lines.append(f"{INDENT}}}")

    lines += ["", f"{INDENT}education {{"]
    lines += [
        f"{INDENT * 2}{quote(degree['title'])} at {quote(degree['organization'])}"
        f" from {degree['start']} to {degree['end']};"
        for degree in data["education"]
    ]
    lines.append(f"{INDENT}}}")

    lines += ["", f"{INDENT}classification {{"]
    lines += [f"{INDENT * 2}{p} -> {'ACCEPTED' if verdicts[p] else 'REJECTED'};" for p in PROFILES]
    if not any(verdicts.values()):
        lines.append(f"{INDENT * 2}UNQUALIFIED -> ACCEPTED;")
    lines += [f"{INDENT}}}", "}"]
    return "\n".join(lines) + "\n"
