# ResumeLens

Formal language-based résumé screening. Computación y Estructuras Discretas III,
Universidad Icesi, 2026-2.

ResumeLens reads a plain-text résumé and decides, for each of four professional
profiles, whether the qualifications written in it satisfy the pattern of the profile.
It does not rank candidates or make hiring decisions. Each stage uses a formal model:

| Stage | Formal model | Module | Document |
|---|---|---|---|
| 1. Extraction | Regular expressions (`re`) | `extractor.py` | [regular_expressions.md](docs/regular_expressions.md) |
| 2. Normalization | Finite-state transducer (pyformlang) | `normalizer.py` | [transducers.md](docs/transducers.md) |
| 3. Recognition | Deterministic finite automata (pyformlang) | `classifier.py` | [automata.md](docs/automata.md) |
| 4. Candidate profile | Context-free grammar (textX) | `dsl_generator.py`, `parser.py`, `validator.py`, `markdown_generator.py` | [grammar.md](docs/grammar.md), [metamodel.md](docs/metamodel.md) |

## Team

| Member | GitHub |
|---|---|
| Maria Juliana Marin Shek | [@Majumashe](https://github.com/Majumashe) |
| Juan Pablo Gamboa | [@JuanPabloGam](https://github.com/JuanPabloGam) |
| Bryan Moreno Diaz | [@brynzd](https://github.com/brynzd) |

IDE: Visual Studio Code.

## The DSL in ResumeLens

The candidate profile DSL is the output of the pipeline. A `.resume` document records
what ResumeLens found about one candidate: the information extracted in stage 1, the
canonical skills of stage 2 and the verdict of each profile from stage 3.
`src/dsl_generator.py` writes the document, textX parses it with
[`grammar/resume.tx`](grammar/resume.tx), the validator rejects it if it breaks a
lexical, syntactic or semantic rule, and the Markdown generator renders the valid ones.

## Language

A document is one `candidate "Name" { ... }` block with its sections in a fixed order:
header (headline, location and an optional summary), contact (email, phone and/or
LinkedIn), skills (canonical tokens separated by commas), optional languages,
experience and education records with their periods, and the classification with the
verdict of each profile.

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

### Profiles

| Profile | Pattern |
|---|---|
| `FULL_STACK_DEVELOPER` | JavaScript/TypeScript → frontend framework → backend → database → Git |
| `MACHINE_LEARNING_ENGINEER` | Python → data library → ML framework → database → Git |
| `FRONTEND_DEVELOPER` (team) | JavaScript/TypeScript → UI framework → styling → Git |
| `DATA_ENGINEER` (team) | Python/Scala → pipeline technology → database → Git |

The profiles are data in [`src/profiles.py`](src/profiles.py), processed by the same
pipeline. A résumé that no profile accepts is `UNQUALIFIED`.

## Project structure

```
ResumeLens/
├── grammar/resume.tx         textX grammar of the DSL
├── src/
│   ├── profiles.py           the four profiles
│   ├── extractor.py          stage 1
│   ├── normalizer.py         stage 2
│   ├── classifier.py         stage 3
│   ├── dsl_generator.py      stage 4: writes the .resume document
│   ├── parser.py             stage 4: parses a .resume file
│   ├── validator.py          stage 4: lexical, syntactic and semantic validation
│   ├── markdown_generator.py stage 4: Markdown visualization
│   ├── pipeline.py           the four stages from the command line
│   ├── app.py                web interface (Streamlit)
│   └── diagrams.py           generates docs/diagrams/
├── data/resumes/             plain-text résumés, input of the pipeline
├── examples/                 the three DSL examples
├── output/                   Markdown of the examples
├── docs/                     design documents, diagrams and poster
└── tests/                    pytest suite, and valid/ and invalid/ DSL documents
```

## Requirements

- Python 3.10 or newer (tested with 3.12 and 3.14).
- textX 4.4.0, pyformlang 1.0.11, Streamlit 1.64.0, pandas 2.3.3 and pytest 8.4.2
  ([`requirements.txt`](requirements.txt)).
- [Graphviz](https://graphviz.org/download/), only to render the diagrams.

## Installation

```bash
git clone https://github.com/brynzd/ResumeLens.git
cd ResumeLens
python3 -m venv .venv            # python3 must be 3.10 or newer
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Web interface, with one tab per stage:

```bash
streamlit run src/app.py
```

The whole pipeline on plain-text résumés. It prints every stage and writes the
extracted data (`.json`), the candidate document (`.resume`) and its Markdown to
`output/pipeline/`:

```bash
python src/pipeline.py data/resumes/wednesday.txt
```

### Run the parser

```bash
python src/parser.py examples/resume_01.resume
```

It prints a summary of the model, or the error with its line and column.

### Generate the Markdown

```bash
python src/markdown_generator.py examples/resume_01.resume
```

It validates the document and writes `output/resume_01.md`.

### Validation and tests

```bash
python src/validator.py    # examples/ and tests/valid/ accepted, tests/invalid/ rejected
python -m pytest
```

### Diagrams

```bash
python src/diagrams.py     # the PNG files need Graphviz
```

## Examples

The pipeline generated the three examples from the résumés of `data/resumes/`. Their
Markdown is in `output/` and their parse trees in `docs/diagrams/`.

- [`resume_01.resume`](examples/resume_01.resume): Wednesday Addams, reference résumé 1
  of the assignment. Only `FULL_STACK_DEVELOPER` is accepted.
- [`resume_02.resume`](examples/resume_02.resume): Mary Jane Watson, reference résumé 2.
  Only `MACHINE_LEARNING_ENGINEER` is accepted.
- [`resume_03.resume`](examples/resume_03.resume): Peter Parker. It uses every contact
  field, the languages section, two experiences and two degrees, and has two accepted
  profiles: `FULL_STACK_DEVELOPER` and `FRONTEND_DEVELOPER`.

## Documentation

| Document | Content |
|---|---|
| [design.md](docs/design.md) | requirements, modules, functions, inputs and outputs |
| [regular_expressions.md](docs/regular_expressions.md), [transducers.md](docs/transducers.md), [automata.md](docs/automata.md) | formalization of stages 1 to 3 |
| [grammar.md](docs/grammar.md) | stage 4: domain, EBNF and Chomsky Normal Form of part of the grammar |
| [metamodel.md](docs/metamodel.md) | stage 4: metamodel and parse trees |
| [test_cases.md](docs/test_cases.md) | test cases and scenarios |
| [literature_review.md](docs/literature_review.md) | literature review |
| [ai_usage_log.md](docs/ai_usage_log.md) | use of generative AI |
| [POSTER.pdf](docs/poster/POSTER.pdf) | research poster |

## Authors

Maria Juliana Marin Shek, Juan Pablo Gamboa and Bryan Moreno Diaz.
