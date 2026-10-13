"""The ResumeLens pipeline, from a plain-text résumé to its candidate document.

résumé text -> stage 1: extraction (regular expressions)
            -> stage 2: normalization (finite-state transducer)
            -> stage 3: recognition (one DFA per profile)
            -> stage 4: candidate profile document validated with textX
            -> Markdown visualization

Usage:
    python src/pipeline.py data/resumes/wednesday.txt [more résumés ...]

For every résumé it prints the result of each stage and writes to
output/pipeline/ the extracted information (<name>.json), the candidate
document (<name>.resume) and, when the document is valid, its Markdown
visualization (<name>.md).
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


def run_pipeline(text, metamodel=None):
    """Run the four stages on a résumé text and return every intermediate result."""
    data = extract_resume_entities(text)
    tokens, unknown = normalize(data["technologies"])
    sequences = {p: sort_for_profile(tokens, p) for p in PROFILES}
    verdicts = {p: evaluate_resume_profile(sequences[p], p) for p in PROFILES}
    result = {
        "extracted": data,
        "translations": {raw: translate(raw) for raw in data["technologies"]},
        "tokens": tokens,
        "unknown": unknown,
        "sequences": sequences,
        "traces": {p: trace(sequences[p], p) for p in PROFILES},
        "verdicts": verdicts,
        "missing": missing_information(data, tokens),
        "document": build_resume(data, tokens, verdicts),
        "error": None,
        "markdown": None,
    }
    try:
        model = (metamodel or get_validating_metamodel()).model_from_str(result["document"])
    except TextXError as err:
        result["error"] = f"{type(err).__name__} {err.line}:{err.col}: {err.message}"
    else:
        result["markdown"] = generate_markdown(model)
    return result


def report(name, result):
    """Print the result of every stage."""
    data = result["extracted"]
    print(f"== {name}")
    print("Stage 1 - extraction (regular expressions)")
    print(f"   candidate: {data['personal']['name']} | years of experience: {data['experience_years']}")
    print(f"   skills as written: {', '.join(data['technologies']) or '-'}")
    print("Stage 2 - normalization (finite-state transducer)")
    print(f"   canonical tokens: {', '.join(result['tokens']) or '-'}")
    print(f"   unknown strings:  {', '.join(result['unknown']) or '-'}")
    print("Stage 3 - recognition (one DFA per profile)")
    for profile in PROFILES:
        verdict = "ACCEPTED" if result["verdicts"][profile] else "REJECTED"
        path = " -> ".join(result["traces"][profile])
        print(f"   {profile:26} {verdict:8} {', '.join(result['sequences'][profile]) or '(empty)'}  [{path}]")
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
        save_extracted_data(result["extracted"], str(OUTPUT_DIR / f"{path.stem}.json"))
        (OUTPUT_DIR / f"{path.stem}.resume").write_text(result["document"], encoding="utf-8")
        if result["markdown"] is not None:
            (OUTPUT_DIR / f"{path.stem}.md").write_text(result["markdown"], encoding="utf-8")
        report(path.name, result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/pipeline.py <resume.txt> [more résumés ...]")
        sys.exit(1)
    main(sys.argv[1:])
