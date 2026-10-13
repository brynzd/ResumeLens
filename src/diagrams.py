"""Generate the diagrams of docs/diagrams/ from the code.

- resume_meta: the metamodel of grammar/resume.tx (textX);
- resume_NN_tree: the model of every example in examples/ (textX);
- dfa_*: the transition diagram of every profile DFA;
- fst_normalization: the normalization transducer.

Every .dot file is rendered to .png when Graphviz (dot) is installed.

Usage:
    python src/diagrams.py
"""

import shutil
import subprocess

from textx.export import metamodel_export, model_export

from normalizer import VARIANTS
from parser import PROJECT_ROOT, get_metamodel
from profiles import PROFILE_PATTERNS

DIAGRAMS = PROJECT_ROOT / "docs" / "diagrams"

DFA_NAMES = {
    "FULL_STACK_DEVELOPER": "dfa_full_stack",
    "MACHINE_LEARNING_ENGINEER": "dfa_machine_learning",
    "FRONTEND_DEVELOPER": "dfa_frontend",
    "DATA_ENGINEER": "dfa_data_engineer",
}

STYLE = [
    "    rankdir=LR;",
    '    node [shape=circle, fontname="Helvetica"];',
    '    edge [fontname="Helvetica", fontsize=11];',
    "    start [shape=point];",
]


def dfa_dot(profile):
    """Graphviz source of a profile DFA: per category, an edge and a self-loop."""
    pattern = PROFILE_PATTERNS[profile]
    lines = [f"digraph {profile} {{"] + STYLE
    lines.append(f"    q{len(pattern)} [shape=doublecircle];")
    lines.append("    start -> q0;")
    for i, (_category, tokens) in enumerate(pattern):
        label = " | ".join(tokens)
        lines.append(f'    q{i} -> q{i + 1} [label="{label}"];')
        lines.append(f'    q{i + 1} -> q{i + 1} [label="{label}"];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def fst_dot():
    """Graphviz source of the transducer: one edge per token, labelled inputs / output."""
    lines = ["digraph NORMALIZATION_FST {"] + STYLE
    lines.append("    q1 [shape=doublecircle];")
    lines.append("    start -> q0;")
    for token, spellings in VARIANTS.items():
        lines.append(f'    q0 -> q1 [label="{" | ".join(spellings)} / {token}"];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def main():
    DIAGRAMS.mkdir(parents=True, exist_ok=True)
    dot_files = []

    metamodel = get_metamodel()
    path = DIAGRAMS / "resume_meta.dot"
    metamodel_export(metamodel, str(path))
    dot_files.append(path)
    for example in sorted((PROJECT_ROOT / "examples").glob("*.resume")):
        path = DIAGRAMS / f"{example.stem}_tree.dot"
        model_export(metamodel.model_from_file(example), str(path))
        dot_files.append(path)

    for profile, name in DFA_NAMES.items():
        path = DIAGRAMS / f"{name}.dot"
        path.write_text(dfa_dot(profile), encoding="utf-8")
        dot_files.append(path)
    path = DIAGRAMS / "fst_normalization.dot"
    path.write_text(fst_dot(), encoding="utf-8")
    dot_files.append(path)

    if shutil.which("dot") is None:
        print("Graphviz (dot) is not installed: only the .dot files were written.")
        return
    for path in dot_files:
        subprocess.run(["dot", "-Tpng", str(path), "-o", str(path.with_suffix(".png"))], check=True)
    print(f"Wrote {len(dot_files)} diagrams to docs/diagrams/")


if __name__ == "__main__":
    main()
