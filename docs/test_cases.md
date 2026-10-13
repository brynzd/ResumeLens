# Test Cases

The test cases of ResumeLens: the scenarios of every stage, their input and the
expected result. Every scenario is an automated test of `tests/`.

```bash
python -m pytest          # 89 tests
python src/validator.py   # the 31 DSL documents, with the error of each invalid one
```

## Strategy

- The examples of the assignment are test cases as given: the two résumé fragments,
  the transformation table and the sorting example of stage 2, and the example of
  stage 3.
- One test file per stage, plus the pipeline end to end.
- Positive cases and negative cases, which must be rejected, for every stage.
- Sample résumés in [`data/resumes/`](../data/resumes/): one per profile, one with two
  accepted profiles (Peter Parker), an unqualified candidate with an unknown skill
  (Bart Simpson) and the two fragments of the assignment.

| File | Tests | What it covers |
|---|---|---|
| `test_extractor.py` | 8 | stage 1: regular expressions |
| `test_normalizer.py` | 28 | stage 2: transducer and canonical order |
| `test_classifier.py` | 12 | stage 3: the profile automata |
| `test_dsl.py` | 34 | stage 4: DSL documents and Markdown |
| `test_pipeline.py` | 7 | the four stages end to end |

## Stage 1: extraction (`test_extractor.py`)

| ID | Scenario | Input | Expected |
|---|---|---|---|
| E1 | Example of the assignment | Wednesday Addams fragment | `JS`, `React.js`, `NodeJS`, `Postgres`, `Git`, as written; the name; 3 years |
| E2 | Second reference fragment | Mary Jane Watson fragment | the seven skills; `predictive models` and `data-processing pipelines`; 2 years |
| E3 | Skills by category | Wednesday fragment | languages `JS`; frameworks `React.js`, `NodeJS`; databases `Postgres`; tools `Git` |
| E4 | Personal and contact information | `peter_parker.txt` | headline, location, e-mail, phone and LinkedIn |
| E5 | Professional experience | `peter_parker.txt` | 4 years; two positions, the first one with two tasks |
| E6 | Academic qualifications and languages | `peter_parker.txt` | two degrees; `B.Sc.` and `Diploma`; English native, Spanish professional |
| E7 | Unknown skill in the list | `bart_simpson.txt` | `COBOL` kept as unrecognized |
| E8 | Missing information | Wednesday fragment | no contact, experience or education |

## Stage 2: normalization (`test_normalizer.py`)

| ID | Scenario | Input | Expected |
|---|---|---|---|
| N1 | Transformations of the assignment | the 16 spellings of the table (`JS` … `PyTorch`) in a skills list | each one extracted whole and translated to its token |
| N2 | Transformations of the team | `TypeScript`, `Vue.js`, `Tailwind CSS`, `Spring Boot`, `NumPy`, `Apache Spark`, `Mongo DB`, `Python3` | their tokens |
| N3 | Unknown strings | `Git`, `COBOL`, `Docker` | token `GIT`; unknown `COBOL` and `Docker` |
| N4 | Equivalent spellings | `JS`, `Javascript`, `JavaScript`, `React.js`, `ReactJS` | `JAVASCRIPT`, `REACT` |
| N5 | Sorting example of the assignment | `Git, NodeJS, JS, Postgres, React.js` | `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT` |
| N6 | Each profile keeps its tokens | `Python, Pandas, React, Git` | ML: `PYTHON, PANDAS, GIT`; Frontend: `REACT, GIT` |

## Stage 3: recognition (`test_classifier.py`)

| ID | Scenario | Input | Expected |
|---|---|---|---|
| A1 | Example of the assignment | `PYTHON, PANDAS, TENSORFLOW, POSTGRESQL, GIT` on Machine Learning | ACCEPTED |
| A2 | Full Stack | `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT`; `TYPESCRIPT, ANGULAR, DJANGO, MONGODB, GIT`; without backend | ACCEPTED, ACCEPTED, REJECTED |
| A3 | Machine Learning | with a second library and framework; without ML framework | ACCEPTED, REJECTED |
| A4 | Frontend | `TYPESCRIPT, VUE, TAILWIND, GIT`; without styling | ACCEPTED, REJECTED |
| A5 | Data Engineer | `PYTHON, SPARK, AIRFLOW, POSTGRESQL, GIT`; without pipeline technology | ACCEPTED, REJECTED |
| A6 | Several profiles | Peter Parker's tokens | Full Stack and Frontend |
| A7 | No profile | `GIT` | none |

## Stage 4: candidate profile DSL (`test_dsl.py`)

Every document must be accepted or rejected as expected. The Markdown generated from
each example must also be equal to its `output/resume_NN.md`.

| Document | Scenario | Result |
|---|---|---|
| `examples/resume_01..03` | the three examples | ACCEPTED |
| `tests/valid/full_featured` | every optional part, block comment | ACCEPTED |
| `tests/valid/minimal` | only the mandatory parts | ACCEPTED |
| `tests/valid/unqualified` | every profile rejected, UNQUALIFIED accepted | ACCEPTED |
| `lex_bad_date` | date written `08/2022` | Expected DATE |
| `lex_bad_day` | day 32 | Expected DATE |
| `lex_bad_month` | month 13 | Expected DATE |
| `lex_bad_email` | e-mail without `@` | Expected EMAIL |
| `lex_lowercase_skill` | skill `react` | Expected CANON |
| `syn_bad_keyword` | incorrect keyword `skils` | Expected 'skills' |
| `syn_empty_skills` | empty list | Expected CANON |
| `syn_incomplete_profile` | incomplete candidate profile | Expected 'summary' or 'contact' |
| `syn_invalid_nesting` | education nested in experience | Expected 'in' or '{' or 'role' or '}' |
| `syn_list_missing_comma` | `REACT NODE_JS` in a list | Expected ',' or '}' |
| `syn_list_trailing_comma` | comma after the last skill | Expected CANON |
| `syn_missing_education` | missing mandatory section | Expected 'education' |
| `syn_missing_semicolon` | missing `;` | Expected ';' |
| `syn_unclosed_brace` | the candidate block is never closed | Expected '}' |
| `syn_unknown_profile` | profile `DEVOPS_ENGINEER` | Expected one of the five profiles |
| `syn_wrong_section_order` | skills before contact | Expected 'summary' or 'contact' |
| `sem_empty_name`, `sem_empty_headline`, `sem_blank_location` | missing mandatory information | … cannot be empty |
| `sem_empty_contact` | no contact field | contact needs at least one of: email, phone, linkedin |
| `sem_duplicate_skill` | `GIT` twice | duplicate skill 'GIT' |
| `sem_unknown_skill` | `COBOL` | 'COBOL' is not a canonical skill |
| `sem_period_reversed` | the period ends before it starts | period ends (2018-08) before it starts (2022-05) |
| `sem_duplicate_profile` | a profile classified twice | profile … is classified more than once |
| `sem_verdict_mismatch` | Data Engineer accepted for skills its DFA rejects | DATA_ENGINEER -> ACCEPTED contradicts the profile automaton |

The invalid documents cover the errors the activity lists (missing mandatory
information, incorrect keywords, malformed structures, invalid nesting, incorrect list
syntax and incomplete candidate profiles), plus lexical and semantic errors.

## End to end (`test_pipeline.py`)

Every sample résumé goes through the four stages.

| ID | Résumé | Accepted profiles | Candidate document |
|---|---|---|---|
| P1 | `wednesday.txt` | Full Stack | valid |
| P2 | `mary_jane.txt` | Machine Learning | valid |
| P3 | `peter_parker.txt` | Full Stack, Frontend | valid |
| P4 | `lisa_simpson.txt` | Data Engineer | valid |
| P5 | `bart_simpson.txt` | none (UNQUALIFIED) | valid |
| P6 | `wednesday_fragment.txt` | Full Stack | rejected: no headline, contact, experience or education |
| P7 | `mary_jane_fragment.txt` | Machine Learning | rejected, for the same reason |
