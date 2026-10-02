"""Generate the Markdown visualization of a parsed résumé.

Builds a readable Markdown document from the model produced by ``parser.py``
and writes it to ``output/`` (``examples/resume_01.resume`` ->
``output/resume_01.md``).

Usage:
    python src/markdown_generator.py examples/resume_01.resume
"""

import sys
from pathlib import Path

from parser import PROJECT_ROOT, get_metamodel, parse_file

OUTPUT_DIR = PROJECT_ROOT / "output"


def period_str(period):
    """Format a Period as 'start - end'."""
    return f"{period.start} - {period.end}"


def generate_markdown(c):
    """Return the Markdown text for a CandidateProfile model."""
    lines = [f"# {c.name}", "", f"{c.header.headline} - {c.header.location}", ""]
    if c.header.summary:
        lines += [c.header.summary, ""]

    lines.append("## Contact")
    if c.contact.email:
        lines.append(f"- Email: {c.contact.email}")
    if c.contact.phone:
        lines.append(f"- Phone: {c.contact.phone}")
    if c.contact.linkedin:
        lines.append(f"- LinkedIn: {c.contact.linkedin}")
    lines.append("")

    lines.append("## Skills")
    lines += [f"- {s}" for s in c.skills.items]
    lines.append("")

    if c.languages:
        lines.append("## Languages")
        lines += [f"- {l.name}: {l.level}" for l in c.languages.items]
        lines.append("")

    lines.append("## Experience")
    for exp in c.experiences.items:
        place = f", {exp.location}" if exp.location else ""
        lines.append(f"### {exp.role}")
        lines.append(f"{exp.company}{place} ({period_str(exp.period)})")
        lines += [f"- {t.description}" for t in exp.tasks]
        lines.append("")

    lines.append("## Education")
    lines += [
        f"- {d.degree}, {d.institution} ({period_str(d.period)})"
        for d in c.education.items
    ]
    lines.append("")

    lines.append("## Classification")
    lines += [f"- {r.profile}: {r.verdict}" for r in c.classification.items]
    lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print("Usage: python src/markdown_generator.py <file.resume>")
        sys.exit(1)

    path = Path(sys.argv[1])
    candidate = parse_file(path, get_metamodel())

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / (path.stem + ".md")
    out_path.write_text(generate_markdown(candidate), encoding="utf-8")
    print(f"Markdown written to {out_path}")


if __name__ == "__main__":
    main()
