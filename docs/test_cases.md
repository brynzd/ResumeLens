# Test Cases

Design of the test cases of ResumeLens: the scenarios of every stage, their input,
the expected result and the automated test that checks it.

```bash
python -m pytest          # 278 tests: stages 1-4, pipeline, UI, diagrams, normal form
python src/validator.py   # the 32 DSL specifications, with the error of each invalid one
```

## Strategy

- **Reference cases of the assignment first.** The two résumé fragments (Wednesday
  Addams, Mary Jane Watson), the transformation table of stage 2, its sorting
  example and the stage-3 example are test cases as given.
- **One test file per stage**, plus end-to-end tests of the whole pipeline, tests
  of the UI and tests that keep the documentation (diagrams, normal form) consistent
  with the code.
- **Scenarios per stage**: a normal case, alternatives and over-qualification,
  boundary cases, and negative cases that must be rejected.
- **Sample résumés** in [`data/resumes/`](../data/resumes/): one per profile, one
  with two accepted profiles (Peter Parker), one unqualified candidate with an
  unknown skill (Bart Simpson) and the two fragments of the assignment.

| File | Tests | What it covers |
|---|---|---|
| `tests/test_extractor.py` | 58 | stage 1: regular expressions |
| `tests/test_normalizer.py` | 121 | stage 2: transducer, unknown strings, canonical order |
| `tests/test_classifier.py` | 31 | stage 3: the four DFAs |
| `tests/test_dsl.py` | 37 | stage 4: the 32 specifications, Markdown, examples |
| `tests/test_pipeline.py` | 13 | the four stages end to end, command line |
| `tests/test_app.py` | 5 | Streamlit UI (`streamlit.testing`, no browser) |
| `tests/test_diagrams.py` | 8 | diagrams match the code |
| `tests/test_normal_form.py` | 5 | Chomsky Normal Form (RAA3) |

## Stage 1 — extraction (`tests/test_extractor.py`)

| ID | Scenario | Input | Expected |
|---|---|---|---|
| E1 | Reference fragment | Wednesday Addams fragment | `JS`, `React.js`, `NodeJS`, `Postgres`, `Git`, as written and in order; name; 3 years |
| E2 | Reference fragment with TensorFlow | Mary Jane Watson fragment | the seven skills, `TensorFlow` included |
| E3 | Every spelling is one string | `Tensor Flow`, `Py Torch`, `scikit learn`, `Node`, `Vue.js`, `Spring Boot`, … (21 spellings) | exactly that string |
| E4 | Skills by category | Wednesday fragment | languages `JS`; frameworks `React.js`, `NodeJS`; databases `Postgres`; tools `Git` |
| E5 | Whole words only | `Node.js and React.js`, `Next.js`, `PostgreSQL, MySQL, NoSQL`, `GitHub` | no `js` inside `Node.js`; `Next.js` gives nothing; only `PostgreSQL`; nothing |
| E6 | Repeated skill | `React` in the list and in a task | listed once |
| E7 | Unknown listed skill | `Technical Skills: Git, COBOL` | `COBOL` kept as unrecognized |
| E8 | Phone formats | `+57 3101234567`, `+1 (212) 555-0134`, `310-123-4567`, … (7) | the whole number, accepted by the DSL `PHONE` terminal |
| E9 | Not phones | a period `(2018-08 - 2022-05)`, `from 2019 to 2023`, `Room 101` | no phone |
| E10 | Contact | full résumé | e-mail, phone and LinkedIn |
| E11 | Name | name followed by a capitalized line; with an accent; with particles; in capitals; after blank lines; no name line | the first line only, or none |
| E12 | Years of experience | `3 years of experience`, `10+ years …`, `3 años de experiencia`, `Graduated 4 years ago` | 3, 10, 3, none |
| E13 | Sections | full résumé | headline, location; two positions with tasks; two degrees; academic keywords; two languages |
| E14 | Other qualifications | `predictive models`, `REST APIs` | extracted as written |
| E15 | Missing information | Wednesday fragment | contact `None`; no experience, education or languages |

## Stage 2 — normalization (`tests/test_normalizer.py`)

| ID | Scenario | Input | Expected |
|---|---|---|---|
| N1 | Transformation table of the assignment | the 16 inputs (`JS` … `PyTorch`) | the 16 canonical tokens |
| N2 | Same table through stages 1 and 2 | `Technical Skills: <input>.` | the canonical token |
| N3 | Every input symbol is reachable | each of the 57 spellings of Σ, in lowercase, title case and capitals | extracted whole and translated to its token |
| N4 | Other spellings | `Java Script`, `Python3`, `Angular.js`, `Mongo DB`, `PySpark`, `Tensor<TAB>Flow`, … | a token (cleaning collapses spaces) |
| N5 | Strings outside Σ | `COBOL`, `Docker`, `Reac`, `Reactt`, `postgre`, `React Native` | no translation |
| N6 | Unknown strings reported | `Git, COBOL, Docker, COBOL` | tokens `GIT`; unknown `COBOL`, `Docker` |
| N7 | Equivalent spellings | `JS`, `Javascript`, `JavaScript`, `React`, `React.js` | `JAVASCRIPT`, `REACT` |
| N8 | Sorting example of the assignment | `Git, NodeJS, JS, Postgres, React.js` | `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT` |
| N9 | Order independence | the 120 orders of those five skills | one sequence |
| N10 | Projection per profile | `Python, Pandas, React, Git` | ML: `PYTHON, PANDAS, GIT`; Frontend: `REACT, GIT` |
| N11 | 7-tuple | the transducer | Q = {q₀, q₁}, q₀ initial, F = {q₁}, \|Σ\| = 57, Γ = 23 tokens |
| N12 | Shared vocabulary | Γ, the DSL skills, the profiles | Γ = DSL vocabulary; every profile uses tokens of Γ |
| N13 | Unknown profile | `DEVOPS_ENGINEER` | error |

## Stage 3 — recognition (`tests/test_classifier.py`)

| ID | Scenario | Input | Expected |
|---|---|---|---|
| A1 | Stage-3 example of the assignment | `PYTHON, PANDAS, TENSORFLOW, POSTGRESQL, GIT` on Machine Learning | ACCEPTED |
| A2 | Same example written as a résumé | `Python, Pandas, TensorFlow, Postgres, Git` | only Machine Learning accepted |
| A3 | Reference fragments | Wednesday, Mary Jane | only Full Stack; only Machine Learning |
| A4 | Patterns, alternatives and extras | 8 sequences over the four profiles (TypeScript/Angular/Django/MongoDB, SQL as Full Stack database, extra skills, Scala, …) | ACCEPTED |
| A5 | Missing category | no backend, no Git, no ML framework, no styling, no pipeline | REJECTED |
| A6 | Full Stack with SQL, end to end | `JavaScript, React, Node.js, SQL, Git` | Full Stack accepted |
| A7 | Sequences the DFA rejects | empty; categories out of order; a symbol outside Σ | REJECTED |
| A8 | 5-tuple of each DFA | the four automata | deterministic; \|Q\| = 6, 6, 5, 5; \|Σ\| = 12, 9, 8, 7; two transitions per symbol; one final state |
| A9 | Four verdicts | Wednesday's tokens | Full Stack only |
| A10 | Several profiles | Peter Parker's tokens | Full Stack and Frontend |
| A11 | No profile | `GIT` | none |
| A12 | Run of an automaton | Mary Jane on Machine Learning; `PYTHON, SQL, GIT` on Data Engineer | q₀ q₁ q₂ q₂ q₃ q₃ q₄ q₅; stops at q₁ |

## Stage 4 — candidate profile DSL (`tests/test_dsl.py`, `python src/validator.py`)

Every specification must be accepted or rejected as expected; the error is the one
`python src/validator.py` prints.

| Specification | Scenario | Result |
|---|---|---|
| `examples/resume_01..03` | the three examples | ACCEPTED |
| `tests/valid/full_featured` | every optional part, block comment | ACCEPTED |
| `tests/valid/minimal` | only the mandatory parts | ACCEPTED |
| `tests/valid/unqualified` | every profile rejected, UNQUALIFIED accepted | ACCEPTED |
| `lex_bad_date` | date written `08/2022` | Expected DATE |
| `lex_bad_day` | day 32 | Expected DATE |
| `lex_bad_month` | month 13 | Expected DATE |
| `lex_bad_email` | malformed e-mail | Expected EMAIL |
| `lex_lowercase_skill` | skill `react` | Expected CANON |
| `syn_bad_keyword` | incorrect keyword | Expected 'skills' |
| `syn_empty_skills` | empty list | Expected CANON |
| `syn_incomplete_profile` | incomplete candidate profile | Expected 'summary' or 'contact' |
| `syn_invalid_nesting` | a section nested in an experience | Expected 'in' or '{' or 'role' or '}' |
| `syn_list_missing_comma` | `A B` in a list | Expected ',' or '}' |
| `syn_list_trailing_comma` | `A, B,` | Expected CANON |
| `syn_missing_education` | missing mandatory section | Expected 'education' |
| `syn_missing_semicolon` | missing `;` | Expected ';' |
| `syn_unclosed_brace` | malformed structure | Expected '}' |
| `syn_unknown_profile` | profile outside the vocabulary | Expected one of the five profiles |
| `syn_wrong_section_order` | sections out of order | Expected 'summary' or 'contact' |
| `sem_empty_name`, `sem_empty_headline`, `sem_blank_location` | missing mandatory information | … cannot be empty |
| `sem_empty_contact` | no contact field | contact needs at least one of: email, phone, linkedin |
| `sem_duplicate_skill` | `GIT` twice | duplicate skill 'GIT' |
| `sem_unknown_skill` | `COBOL` | 'COBOL' is not a canonical skill |
| `sem_period_reversed` | period ends before it starts | period ends (2018-08) before it starts (2022-05) |
| `sem_duplicate_profile` | a profile classified twice | profile … is classified more than once |
| `sem_unqualified_conflict` | UNQUALIFIED accepted with a profile | UNQUALIFIED cannot be ACCEPTED together with another profile |
| `sem_verdict_mismatch` | Data Engineer accepted for skills its DFA rejects | DATA_ENGINEER -> ACCEPTED contradicts the profile automaton |

The invalid specifications cover every error the activity lists: missing mandatory
information, incorrect keywords, malformed structures, invalid nesting, incorrect
list syntax and incomplete candidate profiles, plus lexical and semantic errors.

Also in `tests/test_dsl.py`: every `output/resume_NN.md` equals the Markdown
generated from its example, there are at least three examples, and together they
use languages, several experiences and degrees, every contact field and different
classifications.

## End to end (`tests/test_pipeline.py`)

| ID | Scenario | Input | Expected |
|---|---|---|---|
| P1 | The examples are pipeline output | `wednesday.txt`, `mary_jane.txt`, `peter_parker.txt` | exactly `examples/resume_01..03.resume` (without the comment line) |
| P2 | Every sample résumé | the seven files of `data/resumes/` | accepted profiles: Full Stack; ML; Full Stack and Frontend; Data Engineer; none; and valid document for all but the fragments |
| P3 | Reference fragments | `wednesday_fragment.txt`, `mary_jane_fragment.txt` | accepted by their DFA; document rejected by textX; missing headline, location, contact, experience, education |
| P4 | Unqualified candidate | `bart_simpson.txt` | unknown `COBOL`; `UNQUALIFIED -> ACCEPTED`; valid document |
| P5 | Command line | two résumés | `.json`, `.resume` (and `.md` when valid) per résumé; every stage printed |

## User interface (`tests/test_app.py`)

| ID | Scenario | Expected |
|---|---|---|
| U1 | First load | asks for a résumé |
| U2 | Sample résumé (Wednesday) | four tabs; Full Stack ACCEPTED, Data Engineer REJECTED; the generated document; textX accepts it |
| U3 | Peter Parker | "Accepted profiles: Full Stack Developer, Frontend Developer" |
| U4 | Pasted reference fragment | Full Stack ACCEPTED; warning with the missing parts; textX rejects the document |
| U5 | Bart Simpson | UNQUALIFIED |

## Diagrams and normal form

- `tests/test_diagrams.py`: the four DFA diagrams equal the ones generated from
  `PROFILE_PATTERNS`, the transducer diagram equals the one generated from
  `VARIANTS`, and every example has its parse tree (`.dot` and `.png`).
- `tests/test_normal_form.py`: the CNF of [`normal_forms.md`](normal_forms.md) is in
  normal form and accepts and rejects the same strings as the original grammar.
