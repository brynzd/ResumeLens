# ResumeLens
### Formal Language-Based Resume Screening

Computación y Estructuras Discretas III — Universidad Icesi — 2026-2

ResumeLens is a résumé-screening system that applies formal language models (regular expressions, finite-state transducers, finite automata and context-free grammars) to extract, normalize and recognize candidate qualifications. Its candidate profile DSL represents the structured information the system produces: personal and contact information, experience, education, normalized skills and the profile classification. The language is specified with an EBNF grammar, implemented with [textX](https://textx.github.io/textX/), validated, and rendered as Markdown.

## Team

| Member | GitHub |
|---|---|
| Maria Juliana Marin Shek | [@Majumashe](https://github.com/Majumashe) |
| Juan Pablo Gamboa | — |
| Bryan Moreno Diaz | [@brynzd](https://github.com/brynzd) |

## The DSL inside ResumeLens

This repository implements **stage 4** of the ResumeLens pipeline: the candidate
profile DSL. The earlier stages produce the data the DSL represents:



Stage 1 extracts raw strings (`JS`, `React.js`, `Postgres`, …), stage 2
normalizes them into canonical tokens (`JAVASCRIPT, REACT, NODE_JS,
POSTGRESQL, GIT`), and stage 3 runs one automaton per profile to produce an
`ACCEPTED` / `REJECTED` verdict. A `.resume` document written in the DSL is the
structured record of those results for one candidate, and this repo parses it,
validates it and renders it as Markdown.

## Language

A candidate document is a single `candidate "Name" { ... }` block with a fixed
sequence of sections: header (headline, location, optional summary), contact
(email, phone and/or linkedin), skills (a non-empty list of canonical uppercase
tokens), an optional languages section, experience and education records with
`from ... to ...` periods (`present` allowed as end), and a classification that
pairs each evaluated profile with a verdict. The full EBNF specification is in
[`docs/grammar.md`](docs/grammar.md) and the metamodel in
[`docs/metamodel.md`](docs/metamodel.md).

### Supported profiles

| Profile | Pattern (canonical order) |
|---|---|
| `FULL_STACK_DEVELOPER` | Frontend → Backend → DB → Git |
| `MACHINE_LEARNING_ENGINEER` | Language → Data → ML Framework → DB → Git |
| `FRONTEND_DEVELOPER` | Language → UI Framework → Styles → Git |
| `DATA_ENGINEER` | Language → Pipelines → DB → Git |

## Project structure

```
ResumeLens/
├── README.md
├── requirements.txt
├── grammar/
│   └── resume.tx              # textX grammar of the DSL
├── src/
│   ├── parser.py              # builds the model of a .resume file
│   ├── validator.py           # accepts valid / rejects invalid specifications
│   ├── markdown_generator.py  # renders a parsed résumé as Markdown
│   └── notebooks/             # runnable metamodel walkthrough (Jupyter)
├── examples/                  # résumés written in the DSL (resume_01..03.resume)
├── output/                    # generated Markdown (resume_01..03.md)
├── docs/
│   ├── grammar.md             # EBNF specification: terminals, non-terminals, rules
│   ├── metamodel.md           # metamodel concepts, relationships and diagram
│   ├── domain.md              # domain definition of the candidate profile DSL
│   ├── requirements.md        # functional requirements of ResumeLens
│   ├── assignment/            # assignment statements (PDF)
│   └── diagrams/              # metamodel and parse-tree diagrams
└── tests/
    ├── valid/                 # specifications textX must accept
    └── invalid/               # specifications textX must reject
```

## Setup

Requirements: Python 3.10+, `pip`, and [Graphviz](https://graphviz.org/download/)
(`dot`) to render the diagrams.

```bash
git clone https://github.com/brynzd/ResumeLens.git
cd ResumeLens
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # textX
```

## Usage

Parse a résumé (prints a summary of the model, or the syntax error with line
and column):

```bash
python src/parser.py examples/resume_01.resume
```

Run the validation suite (examples and `tests/valid/` must be accepted,
`tests/invalid/` must be rejected):

```bash
python src/validator.py
```

Generate the Markdown visualization into `output/`:

```bash
python src/markdown_generator.py examples/resume_01.resume
```

Export the metamodel and parse-tree diagrams:

```bash
textx generate grammar/resume.tx --target dot -o docs/diagrams/resume_meta.dot
textx generate examples/resume_01.resume --grammar grammar/resume.tx --target dot -o docs/diagrams/resume_01_tree.dot
dot -Tpng -O docs/diagrams/resume_meta.dot docs/diagrams/resume_01_tree.dot
```


