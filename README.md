# ResumeLens
### Formal Language-Based Resume Screening

Computación y Estructuras Discretas III — Universidad Icesi — 2026-2

ResumeLens is a résumé-screening system that applies formal language models to decide
whether the qualifications written in a résumé satisfy the pattern of a professional
profile. It does not rank candidates or make hiring decisions. A résumé goes through
four stages, each one an explicit formal model:

| Stage | Formal model | What it does | Module | Document |
|---|---|---|---|---|
| 1 | Regular expressions (`re`) | extracts contact information, skills, experience, education, … exactly as written | `src/extractor.py` | [`regular_expressions.md`](docs/regular_expressions.md) |
| 2 | Finite-state transducer (pyformlang) | normalizes every spelling to a canonical token (`JS` → `JAVASCRIPT`) and sorts the tokens in each profile's canonical order | `src/normalizer.py` | [`transducers.md`](docs/transducers.md) |
| 3 | Deterministic finite automata (pyformlang) | one DFA per profile decides ACCEPTED or REJECTED | `src/classifier.py` | [`automata.md`](docs/automata.md) |
| 4 | Context-free grammar (textX) | writes the candidate profile document, validates it and renders it as Markdown | `src/dsl_generator.py`, `src/parser.py`, `src/validator.py`, `src/markdown_generator.py` | [`grammar.md`](docs/grammar.md), [`metamodel.md`](docs/metamodel.md) |

```
résumé.txt ─► regex extraction ─► FST normalization ─► DFA recognition ─► .resume document ─► textX validation ─► Markdown
```

## Team

| Member | GitHub |
|---|---|
| Maria Juliana Marin Shek | [@Majumashe](https://github.com/Majumashe) |
| Juan Pablo Gamboa | [@JuanPabloGam](https://github.com/JuanPabloGam) |
| Bryan Moreno Diaz | [@brynzd](https://github.com/brynzd) |

IDE: Visual Studio Code (with the Python and Jupyter extensions).

## The DSL inside ResumeLens

The candidate profile DSL is the output side of the pipeline. A `.resume` document is
the structured, validated record of everything ResumeLens learned about one candidate:
the information extracted in stage 1, the canonical skills of stage 2 and the verdict
of every profile from stage 3. `src/dsl_generator.py` writes it from a résumé, and a
document can also be written by hand. textX parses it with the grammar in
[`grammar/resume.tx`](grammar/resume.tx), the validator rejects it if it breaks a
lexical, syntactic or semantic rule (including a verdict that contradicts its profile
automaton), and the Markdown generator renders the valid ones.

## Language

A candidate document is a single `candidate "Name" { ... }` block with a fixed
sequence of sections: header (headline, location, optional summary), contact
(email, phone and/or linkedin), skills (a non-empty list of canonical uppercase
tokens), an optional languages section, experience and education records with
`from ... to ...` periods (`present` allowed as end), and a classification that
pairs each evaluated profile with a verdict. The full EBNF specification and the
structural characteristics of the language are in [`docs/grammar.md`](docs/grammar.md),
the metamodel in [`docs/metamodel.md`](docs/metamodel.md) and the domain concepts in
[`docs/domain.md`](docs/domain.md).

```
candidate "Wednesday Addams" {
    headline: "Full Stack Developer";
    location: "Jericho, Vermont";
    contact { email: wednesday@nevermore.edu; }
    skills { JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT }
    experience { role "Software Developer" at "Nevermore Academy" from 2022-08 to present }
    education { "B.Sc. in Computer Science" at "Nevermore Academy" from 2018-08 to 2022-05; }
    classification { FULL_STACK_DEVELOPER -> ACCEPTED; }
}
```

### Supported profiles

| Profile | Pattern (categories in canonical order) |
|---|---|
| `FULL_STACK_DEVELOPER` | Language (JS/TS) → Frontend → Backend → Database (SQL or NoSQL) → Git |
| `MACHINE_LEARNING_ENGINEER` | Python → Data library → ML framework → Database → Git |
| `FRONTEND_DEVELOPER` (team-defined, software engineering) | Language (JS/TS) → UI framework → Styling → Git |
| `DATA_ENGINEER` (team-defined, AI/data) | Language (Python/Scala) → Pipeline technology → Database → Git |

The four profiles are data ([`src/profiles.py`](src/profiles.py)) processed by the same
pipeline; a résumé gets a verdict for each of them, and `UNQUALIFIED` when none accepts.

## Project structure

```
ResumeLens/
├── README.md
├── requirements.txt
├── pytest.ini
├── grammar/
│   └── resume.tx              # textX grammar of the DSL
├── src/
│   ├── extractor.py           # stage 1: regular expressions
│   ├── normalizer.py          # stage 2: finite-state transducer + canonical order
│   ├── classifier.py          # stage 3: one DFA per profile
│   ├── profiles.py            # the four profiles, as data
│   ├── dsl_generator.py       # writes the .resume document from stages 1-3
│   ├── parser.py              # stage 4: builds the model of a .resume file
│   ├── validator.py           # stage 4: lexical, syntactic and semantic validation
│   ├── markdown_generator.py  # stage 4: Markdown visualization
│   ├── pipeline.py            # the four stages on a résumé (command line)
│   ├── app.py                 # web UI (Streamlit)
│   ├── diagrams.py            # generates docs/diagrams/
│   └── notebooks/             # runnable metamodel walkthrough (Jupyter)
├── data/resumes/              # plain-text sample résumés (pipeline input)
├── examples/                  # résumés written in the DSL (resume_01..03.resume)
├── output/                    # Markdown of the examples (resume_01..03.md)
│   └── pipeline/              # what python src/pipeline.py data/resumes/*.txt writes
├── docs/
│   ├── requirements.md        # functional requirements
│   ├── design.md              # modules, functions, inputs and outputs
│   ├── regular_expressions.md # stage 1
│   ├── transducers.md         # stage 2: 7-tuple and diagram
│   ├── automata.md            # stage 3: 5-tuples and diagrams
│   ├── domain.md              # concepts of the candidate profile DSL
│   ├── grammar.md             # stage 4: EBNF, terminals, non-terminals, structure
│   ├── metamodel.md           # metamodel and parsed models
│   ├── normal_forms.md        # Chomsky Normal Form of part of the grammar (RAA3)
│   ├── test_cases.md          # test design and scenarios
│   ├── literature_review.md
│   ├── ai_usage_log.md        # use of generative AI
│   ├── diagrams/              # metamodel, parse trees, automata and transducer
│   ├── poster/                # research poster
│   └── assignment/            # assignment statements (PDF)
└── tests/
    ├── test_*.py              # pytest suite of every stage, the pipeline and the UI
    ├── valid/                 # specifications textX must accept
    └── invalid/               # specifications textX must reject
```

## Requirements

- Python 3.10 or newer (Streamlit 1.64 requires it); tested with Python 3.12 and 3.14.
- The libraries of [`requirements.txt`](requirements.txt): textX 4.4.0, pyformlang
  1.0.11, Streamlit 1.64.0, pandas 2.3.3 and pytest 8.4.2.
- Optional: [Graphviz](https://graphviz.org/download/) (`dot`), only to render the
  diagrams to PNG (`brew install graphviz` on macOS).

## Installation

```bash
git clone https://github.com/brynzd/ResumeLens.git
cd ResumeLens
python3 -m venv .venv            # any Python 3.10+, e.g. python3.12 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

On macOS the system `python3` may be 3.9; use a newer one (for example
`python3.12` from Homebrew) to create the virtual environment.

## Usage

**Web interface** — choose a sample résumé, paste one or upload a `.txt`, and follow
the four stages (one tab per stage):

```bash
streamlit run src/app.py
```

**Whole pipeline from the command line** — prints every stage and writes the
extraction (`.json`), the candidate document (`.resume`) and its Markdown (`.md`) to
`output/pipeline/`:

```bash
python src/pipeline.py data/resumes/wednesday.txt
python src/pipeline.py data/resumes/*.txt
```

**Run the parser** on a DSL document (prints a summary of the model, or the error with
line and column):

```bash
python src/parser.py examples/resume_01.resume
```

**Generate the Markdown** visualization into `output/` (only for a valid document):

```bash
python src/markdown_generator.py examples/resume_01.resume
```

**Run the validation suite** (the examples and `tests/valid/` must be accepted,
`tests/invalid/` rejected, each with its error):

```bash
python src/validator.py
```

**Run the tests** of every stage, the pipeline and the UI:

```bash
python -m pytest
```

**Regenerate the diagrams** of `docs/diagrams/` (the PNG files need Graphviz):

```bash
python src/diagrams.py
```

## Candidate profile examples

The three examples are the documents the pipeline writes from the plain-text résumés
of `data/resumes/` (the tests check it); their Markdown is in `output/` and their parse
trees in `docs/diagrams/`.

- [`resume_01.resume`](examples/resume_01.resume) — **Wednesday Addams**, reference
  résumé 1 of the assignment (`wednesday.txt`). E-mail and LinkedIn, one experience
  with two tasks, one degree. Only `FULL_STACK_DEVELOPER` is accepted.
- [`resume_02.resume`](examples/resume_02.resume) — **Mary Jane Watson**, reference
  résumé 2 (`mary_jane.txt`). E-mail and phone, seven skills, of which the second data
  library and ML framework are extras. Only `MACHINE_LEARNING_ENGINEER` is accepted:
  Data Engineer is rejected because she has no pipeline technology.
- [`resume_03.resume`](examples/resume_03.resume) — **Peter Parker**, the team-defined
  Frontend profile (`peter_parker.txt`). Every contact field, a `languages` section,
  two experiences (the second without tasks), two degrees, a `YYYY-MM-DD` date, and two
  accepted profiles: `FULL_STACK_DEVELOPER` and `FRONTEND_DEVELOPER`.

`data/resumes/` also has a Data Engineer (`lisa_simpson.txt`), an unqualified candidate
with an unknown skill (`bart_simpson.txt`) and the two fragments of the assignment
(`wednesday_fragment.txt`, `mary_jane_fragment.txt`): their profile accepts them, but
they lack the contact, experience and education a candidate document requires, so
textX rejects the document as incomplete.

## Documentation

| Document | Content |
|---|---|
| [`requirements.md`](docs/requirements.md) | functional requirements FR-01 to FR-24 |
| [`design.md`](docs/design.md) | architecture, modules, functions, inputs and outputs, design decisions |
| [`regular_expressions.md`](docs/regular_expressions.md) | stage 1: every regular expression and the language it recognizes |
| [`transducers.md`](docs/transducers.md) | stage 2: the 7-tuple, the diagram and the canonical orders |
| [`automata.md`](docs/automata.md) | stage 3: the 5-tuple, type, diagram and pattern of each automaton |
| [`domain.md`](docs/domain.md), [`grammar.md`](docs/grammar.md), [`metamodel.md`](docs/metamodel.md) | stage 4: concepts, EBNF and structure, metamodel and parse trees |
| [`normal_forms.md`](docs/normal_forms.md) | Chomsky Normal Form of the classification grammar (RAA3) |
| [`test_cases.md`](docs/test_cases.md) | test design, scenarios and expected results |
| [`literature_review.md`](docs/literature_review.md) | literature review |
| [`ai_usage_log.md`](docs/ai_usage_log.md) | record of the use of generative AI |
| [`poster/POSTER.pdf`](docs/poster/POSTER.pdf) | research poster |

## Authors

- Maria Juliana Marin Shek
- Juan Pablo Gamboa
- Bryan Moreno Diaz
