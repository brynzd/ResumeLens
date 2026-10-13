"""Markdown visualization of a valid .resume file.

The file is validated first (lexical, syntactic and semantic rules); an invalid
file is reported and nothing is written.

Usage:
    python src/markdown_generator.py examples/resume_01.resume   (writes output/resume_01.md)
"""

import sys
from pathlib import Path

from textx.exceptions import TextXError

from parser import PROJECT_ROOT, parse_file
from validator import get_validating_metamodel

OUTPUT_DIR = PROJECT_ROOT / "output"


def period_text(period):
    return f"{period.start} - {period.end}"


def generate_markdown(candidate):
    """Markdown text of a candidate model."""
    header = candidate.header
    contact = candidate.contact

    lines = [f"# {candidate.name}", "", f"{header.headline} - {header.location}", ""]
    if header.summary:
        lines += [header.summary, ""]

    lines.append("## Contact")
    if contact.email:
        lines.append(f"- Email: {contact.email}")
    if contact.phone:
        lines.append(f"- Phone: {contact.phone}")
    if contact.linkedin:
        lines.append(f"- LinkedIn: {contact.linkedin}")
    lines.append("")

    lines.append("## Skills")
    for skill in candidate.skills.items:
        lines.append(f"- {skill}")
    lines.append("")

    if candidate.languages:
        lines.append("## Languages")
        for language in candidate.languages.items:
            lines.append(f"- {language.name}: {language.level}")
        lines.append("")

    lines.append("## Experience")
    for job in candidate.experiences.items:
        place = f", {job.location}" if job.location else ""
        lines.append(f"### {job.role}")
        lines.append(f"{job.company}{place} ({period_text(job.period)})")
        for task in job.tasks:
            lines.append(f"- {task.description}")
        lines.append("")

    lines.append("## Education")
    for degree in candidate.education.items:
        lines.append(f"- {degree.degree}, {degree.institution} ({period_text(degree.period)})")
    lines.append("")

    lines.append("## Classification")
    for result in candidate.classification.items:
        lines.append(f"- {result.profile}: {result.verdict}")
    lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print("Usage: python src/markdown_generator.py <file.resume>")
        sys.exit(1)

    path = Path(sys.argv[1])
    try:
        candidate = parse_file(path, get_validating_metamodel())
    except TextXError as err:
        print(f"{path}:{err.line}:{err.col}: invalid résumé: {err.message}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / (path.stem + ".md")
    out_path.write_text(generate_markdown(candidate), encoding="utf-8")
    print(f"Markdown written to {out_path}")


if __name__ == "__main__":
    main()
