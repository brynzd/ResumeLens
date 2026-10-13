"""Write the candidate profile document (.resume) from the results of stages 1 to 3.

Nothing is invented: a mandatory part the résumé lacks is written empty, and
textX rejects the document as an incomplete candidate profile.
"""

from normalizer import GLOBAL_ORDER
from profiles import PROFILES


def quote(text):
    """Write a text as a DSL STRING (double quotes inside become single quotes)."""
    text = (text or "").replace("\\", "/").replace('"', "'")
    return f'"{text}"'


def missing_information(data, tokens):
    """Mandatory parts of the document that the résumé does not provide."""
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


def section(name, body):
    """Lines of a block 'name { ... }' with its body indented."""
    lines = ["", f"    {name} {{"]
    for line in body:
        lines.append("        " + line)
    lines.append("    }")
    return lines


def experience_body(jobs):
    body = []
    for job in jobs:
        role = (f"role {quote(job['title'])} at {quote(job['organization'])}"
                f" from {job['start']} to {job['end']}")
        if job["tasks"]:
            body.append(role + " {")
            for task in job["tasks"]:
                body.append(f"    - {quote(task)}")
            body.append("}")
        else:
            body.append(role)
    return body


def build_resume(data, tokens, verdicts):
    """Text of the candidate document for the extracted data, tokens and verdicts."""
    personal = data["personal"]
    contact = data["contact"]

    lines = [f"candidate {quote(personal['name'])} {{"]
    lines.append(f"    headline: {quote(personal['headline'])};")
    lines.append(f"    location: {quote(personal['location'])};")
    if personal["summary"]:
        lines.append(f"    summary: {quote(personal['summary'])};")

    contact_body = []
    for field in ("email", "phone", "linkedin"):
        if contact[field]:
            contact_body.append(f"{field}: {contact[field]};")
    lines += section("contact", contact_body)

    skills = [token for token in GLOBAL_ORDER if token in tokens]
    lines += section("skills", [", ".join(skills)])

    if data["languages"]:
        languages_body = []
        for language in data["languages"]:
            languages_body.append(f"{quote(language['name'])}: {language['level']};")
        lines += section("languages", languages_body)

    lines += section("experience", experience_body(data["experience"]))

    education_body = []
    for degree in data["education"]:
        education_body.append(f"{quote(degree['title'])} at {quote(degree['organization'])}"
                              f" from {degree['start']} to {degree['end']};")
    lines += section("education", education_body)

    classification_body = []
    for profile in PROFILES:
        verdict = "ACCEPTED" if verdicts[profile] else "REJECTED"
        classification_body.append(f"{profile} -> {verdict};")
    if not any(verdicts.values()):
        classification_body.append("UNQUALIFIED -> ACCEPTED;")
    lines += section("classification", classification_body)

    lines.append("}")
    return "\n".join(lines) + "\n"
