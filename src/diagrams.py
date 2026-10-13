"""Generate the diagrams of docs/diagrams/ from the code.

- resume_meta.dot: the textX metamodel of grammar/resume.tx;
- resume_NN_tree.dot: the parsed model of every example in examples/;
- dfa_<profile>.dot: the transition diagram of every profile DFA;
- fst_normalization.dot: the normalization transducer of stage 2.

When Graphviz is installed (the ``dot`` command), every .dot file is also
rendered to PNG: <name>.dot.png for the textX diagrams (the name
``dot -Tpng -O`` gives) and <name>.png for the automata.

Usage:
    python src/diagrams.py
"""

import re
import shutil
import subprocess

from textx.export import metamodel_export, model_export

from normalizer import VARIANTS
from parser import PROJECT_ROOT, get_metamodel
from profiles import PROFILE_PATTERNS

DIAGRAMS = PROJECT_ROOT / "docs" / "diagrams"

# Profile -> name of its transition diagram.
DFA_FILES = {
    "FULL_STACK_DEVELOPER": "dfa_full_stack",
    "MACHINE_LEARNING_ENGINEER": "dfa_machine_learning",
    "FRONTEND_DEVELOPER": "dfa_frontend",
    "DATA_ENGINEER": "dfa_data_engineer",
}

AUTOMATON_STYLE = [
    "    rankdir=LR;",
    '    node [shape=circle, fontname="Helvetica"];',
    '    edge [fontname="Helvetica", fontsize=11];',
    "    start [shape=point];",
]

# textX names the nodes after Python object ids, which change on every run.
TEXTX_NODE_ID = re.compile(r"(?m)^\d{6,}(?=[\[ ])|(?<=-> )\d{6,}")


def stable_ids(path):
    """Renumber the nodes of a textX diagram (n1, n2, ...) in order of appearance."""
    ids = {}
    text = TEXTX_NODE_ID.sub(lambda m: ids.setdefault(m.group(), f"n{len(ids) + 1}"), path.read_text())
    path.write_text(text, encoding="utf-8")


def dfa_dot(profile):
    """Transition diagram of a profile DFA, as built by classifier.create_profile_dfa."""
    pattern = PROFILE_PATTERNS[profile]
    lines = [f"digraph {DFA_FILES[profile][4:].upper()}_DFA {{", *AUTOMATON_STYLE]
    lines += [f"    q{len(pattern)} [shape=doublecircle];", "    start -> q0;"]
    for i, (_category, tokens) in enumerate(pattern):
        label = " | ".join(tokens)
        lines.append(f'    q{i} -> q{i + 1} [label="{label}"];')
        lines.append(f'    q{i + 1} -> q{i + 1} [label="{label}"];')
    return "\n".join(lines + ["}"]) + "\n"


def fst_dot():
    """Diagram of the normalization transducer: one edge per output token, labelled input / output."""
    lines = ["digraph NORMALIZATION_FST {", *AUTOMATON_STYLE]
    lines += ["    q1 [shape=doublecircle];", "    start -> q0;"]
    for token, spellings in VARIANTS.items():
        lines.append(f'    q0 -> q1 [label="{" | ".join(spellings)} / {token}"];')
    return "\n".join(lines + ["}"]) + "\n"


def render(dot_path, png_path):
    subprocess.run(["dot", "-Tpng", str(dot_path), "-o", str(png_path)], check=True)


def main():
    DIAGRAMS.mkdir(parents=True, exist_ok=True)
    metamodel = get_metamodel()
    textx_files = [DIAGRAMS / "resume_meta.dot"]
    metamodel_export(metamodel, str(textx_files[0]))
    for example in sorted((PROJECT_ROOT / "examples").glob("*.resume")):
        textx_files.append(DIAGRAMS / f"{example.stem}_tree.dot")
        model_export(metamodel.model_from_file(example), str(textx_files[-1]))
    for path in textx_files:
        stable_ids(path)

    automata = [DIAGRAMS / f"{name}.dot" for name in DFA_FILES.values()]
    for profile, path in zip(DFA_FILES, automata):
        path.write_text(dfa_dot(profile), encoding="utf-8")
    automata.append(DIAGRAMS / "fst_normalization.dot")
    automata[-1].write_text(fst_dot(), encoding="utf-8")

    for path in textx_files + automata:
        print(f"wrote {path.relative_to(PROJECT_ROOT)}")
    if shutil.which("dot") is None:
        print("Graphviz (dot) is not installed: the .png files were not rendered.")
        return
    for path in textx_files:
        render(path, path.with_name(path.name + ".png"))
    for path in automata:
        render(path, path.with_suffix(".png"))
    print("rendered every diagram to PNG")


if __name__ == "__main__":
    main()
