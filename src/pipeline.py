"""The ResumeLens pipeline: from a plain-text résumé to its candidate document.

For every résumé it prints the result of each stage and writes to
output/pipeline/ the extracted information (.json), the candidate document
(.resume) and, when the document is valid, its Markdown (.md).

Usage:
    python src/pipeline.py data/resumes/wednesday.txt [more résumés]
"""

import sys
from pathlib import Path

from textx.exceptions import TextXError

from classifier import evaluate_resume_profile, trace
from dsl_generator import build_resume, missing_information
from extractor import extract_resume_entities, save_extracted_data
from markdown_generator import generate_markdown
from normalizer import normalize, sort_for_profile, translate
from parser import PROJECT_ROOT
from profiles import PROFILES
from validator import get_validating_metamodel

OUTPUT_DIR = PROJECT_ROOT / "output" / "pipeline"


def run_pipeline(text, metamodel):
    """Run the four stages on a résumé and return the result of each one."""
    # Stage 1: regular expressions
    data = extract_resume_entities(text)

    # Stage 2: finite-state transducer
    tokens, unknown = normalize(data["technologies"])
    translations = {}
    for raw in data["technologies"]:
        translations[raw] = translate(raw)

    # Stage 3: one DFA per profile, on the tokens in the profile's canonical order
    sequences = {}
    verdicts = {}
    traces = {}
    for profile in PROFILES:
        sequences[profile] = sort_for_profile(tokens, profile)
        verdicts[profile] = evaluate_resume_profile(sequences[profile], profile)
        traces[profile] = trace(sequences[profile], profile)

    # Stage 4: candidate document, validated with textX, and its Markdown
    document = build_resume(data, tokens, verdicts)
    error = None
    markdown = None
    try:
        markdown = generate_markdown(metamodel.model_from_str(document))
    except TextXError as err:
        error = f"{type(err).__name__} {err.line}:{err.col}: {err.message}"

    return {
        "extracted": data,
        "translations": translations,
        "tokens": tokens,
        "unknown": unknown,
        "sequences": sequences,
        "verdicts": verdicts,
        "traces": traces,
        "missing": missing_information(data, tokens),
        "document": document,
        "error": error,
        "markdown": markdown,
    }


def report(name, result):
    """Print the result of every stage."""
    data = result["extracted"]
    print(f"== {name}")
    print("Stage 1 - extraction (regular expressions)")
    print(f"   candidate: {data['personal']['name']}"
          f" | years of experience: {data['experience_years']}")
    print(f"   skills as written: {', '.join(data['technologies']) or '-'}")
    print("Stage 2 - normalization (finite-state transducer)")
    print(f"   canonical tokens: {', '.join(result['tokens']) or '-'}")
    print(f"   unknown strings:  {', '.join(result['unknown']) or '-'}")
    print("Stage 3 - recognition (one DFA per profile)")
    for profile in PROFILES:
        verdict = "ACCEPTED" if result["verdicts"][profile] else "REJECTED"
        sequence = ", ".join(result["sequences"][profile]) or "(empty)"
        states = " -> ".join(result["traces"][profile])
        print(f"   {profile:26} {verdict:8} {sequence}  [{states}]")
    print("Stage 4 - candidate profile document (textX)")
    if result["missing"]:
        print(f"   missing in the résumé: {', '.join(result['missing'])}")
    if result["error"]:
        print(f"   REJECTED: {result['error']}")
    else:
        print("   valid: Markdown visualization generated")
    print()


def main(paths):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metamodel = get_validating_metamodel()
    for name in paths:
        path = Path(name)
        result = run_pipeline(path.read_text(encoding="utf-8"), metamodel)
        save_extracted_data(result["extracted"], OUTPUT_DIR / f"{path.stem}.json")
        (OUTPUT_DIR / f"{path.stem}.resume").write_text(result["document"], encoding="utf-8")
        if result["markdown"] is not None:
            (OUTPUT_DIR / f"{path.stem}.md").write_text(result["markdown"], encoding="utf-8")
        report(path.name, result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/pipeline.py <resume.txt> [more résumés]")
        sys.exit(1)
    main(sys.argv[1:])
