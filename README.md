# ResumeLens

ResumeLens is a résumé-screening system that applies formal language models (regular expressions, finite-state transducers, finite automata and context-free grammars) to extract, normalize and recognize candidate qualifications. Its candidate profile DSL represents the structured information the system produces: personal and contact information, experience, education, normalized skills and the profile classification. The language is specified with an EBNF grammar, implemented with [textX](https://textx.github.io/textX/), validated, and rendered as Markdown.

## Team

<!-- Names and GitHub users. -->

## Language

<!-- Brief description of the candidate profile language. -->

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
│   └── markdown_generator.py  # renders a parsed résumé as Markdown
├── examples/                  # résumés written in the DSL (resume_01..03.resume)
├── output/                    # generated Markdown (resume_01..03.md)
├── docs/
│   ├── grammar.md             # EBNF specification: terminals, non-terminals, rules
│   ├── metamodel.md           # metamodel concepts, relationships and diagram
│   ├── requirements.md        # functional requirements of ResumeLens
│   ├── assignment/            # assignment statements (PDF)
│   └── diagrams/              # parse tree / model diagrams (resume_01..03_tree.png)
└── tests/
    ├── valid/                 # specifications textX must accept
    └── invalid/               # specifications textX must reject
```
