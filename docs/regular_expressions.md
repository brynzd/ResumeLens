# Résumé Information Extraction — Regular Expressions

Stage 1 of the ResumeLens pipeline, implemented with Python's `re` module in
[`src/extractor.py`](../src/extractor.py). It finds the strings of a plain-text
résumé that may represent candidate data or qualifications and keeps them
**exactly as written**. It does not decide whether two strings are equivalent
(stage 2, [`transducers.md`](transducers.md)) or whether the candidate satisfies a
profile (stage 3, [`automata.md`](automata.md)).

## Notation

Every pattern below is a regular expression over the alphabet of characters.
The patterns use Python syntax; its constructs map to the formal operators:

| Python | Formal meaning |
|---|---|
| `ab` | concatenation *a·b* |
| `a\|b` | union *a ∪ b* |
| `a?` | *a ∪ λ* |
| `a+`, `a*` | *a⁺*, *a\** |
| `a{m,n}` | *aᵐ ∪ aᵐ⁺¹ ∪ … ∪ aⁿ* |
| `[abc]`, `\d` | a union of single characters (`\d` = 0 ∪ 1 ∪ … ∪ 9) |
| `(?:…)` | grouping only; `(?P<name>…)` also names the matched part |
| `re.IGNORECASE` | every letter *a* stands for *(a ∪ A)* |

`\b` (word boundary), `^`/`$` (line start/end with `re.MULTILINE`), `\A` (start
of the text) and the lookarounds `(?<!…)`, `(?!…)` are zero-width assertions:
they restrict **where** a match may start or end, but they do not add strings to
the language. `[ \t]` (space or tab) is used instead of `\s` on purpose: `\s`
also matches a line break, which made matches spill into the next line.

## Types of information

| Type of information (assignment) | Patterns | Key in the result |
|---|---|---|
| Personal information | `NAME`, `FIELD` | `personal` |
| Contact information | `EMAIL`, `PHONE`, `LINKEDIN` | `contact` |
| Programming languages | `PROGRAMMING_LANGUAGES` (in `SKILLS`) | `skills.programming_languages` |
| Frameworks and libraries | `FRAMEWORKS_LIBRARIES` (in `SKILLS`) | `skills.frameworks_libraries` |
| Databases | `DATABASES` (in `SKILLS`) | `skills.databases` |
| Tools and technologies | `TOOLS` (in `SKILLS`) | `skills.tools` |
| Other qualifications | `OTHER_QUALIFICATIONS`, `SKILLS_LIST` | `other_qualifications`, `skills.unrecognized` |
| Academic qualifications | `ACADEMIC`, `ENTRY` | `academic_qualifications`, `education` |
| Professional experience | `YEARS`, `ENTRY`, `TASK` | `experience_years`, `experience` |
| Spoken languages | `LANGUAGE` | `languages` |

`technologies` lists every skill string in order of appearance, followed by the
unrecognized items of the skills list: it is the input of stage 2.

---

## 1. Personal information

### Name — `NAME`

```python
NAME_WORD = r"[A-ZÁÉÍÓÚÑÜ][A-Za-zÁÉÍÓÚÑÜáéíóúñü'’-]*"
NAME_PARTICLE = r"(?:de|del|la|las|los|van|von|da|di|y)"
NAME = rf"\A\s*(?P<name>{NAME_WORD}(?:[ \t]+(?:{NAME_PARTICLE}[ \t]+)*{NAME_WORD}){{1,4}})[ \t]*$"
```

**Language.** Let *W* be a word that starts with an uppercase letter (Spanish
accents included) followed by letters, apostrophes or hyphens, *P* a lowercase
particle and *S* one or more spaces or tabs. The name is a string of
*W (S (P S)\* W)ᵏ*, with 1 ≤ *k* ≤ 4 (two to five words), that fills the
**first non-empty line** of the résumé (`\A\s*` before it, only blanks after it).

| Accepted | Rejected |
|---|---|
| `Wednesday Addams` | `Technical Skills:` (the colon is not part of a word) |
| `Mary Jane Watson` | `3 years of experience` (starts with a digit) |
| `Juan Pérez`, `Juan de la Cruz` | `Wednesday` (one word) |
| `WEDNESDAY ADDAMS` | any name that is not on the first line |

### Headline, location and summary — `FIELD`

```python
FIELD = r"^[ \t]*(?P<key>headline|location|summary)[ \t]*:[ \t]*(?P<value>[^\n]*?)[ \t]*$"
# re.MULTILINE | re.IGNORECASE
```

**Language.** Lines `key: value` where *key* ∈ {headline, location, summary} in
any case and *value* is the rest of the line without the surrounding blanks.
The first line of each key is kept; an empty value counts as missing.

## 2. Contact information

### E-mail — `EMAIL`

```python
EMAIL = r"[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"
```

**Language.** *L⁺ @ D (. D)\* . T*, where *L* is a letter, digit or one of
`. _ + -`, *D* a domain label (letters, digits, hyphens) and *T* a top-level
domain of at least two letters. Every match is also accepted by the `EMAIL`
terminal of the DSL. Example: `ana.gomez@icesi.edu.co`.

### Phone — `PHONE`

```python
PHONE = (r"(?<![\w+])(?:\+\d{1,3}(?:[ -]?\(\d{1,4}\))?(?:[ -]?\d{1,4}){2,4}"
         r"|\d{3}[ -]?\d{3}[ -]?\d{4})(?!\d)")
```

**Language.** The union of two sets:

- international numbers: `+`, a country code of one to three digits, an optional
  area code in parentheses, and two to four groups of one to four digits, each
  group optionally preceded by a space or a hyphen;
- ten-digit local numbers, optionally written 3-3-4 with spaces or hyphens.

The lookarounds forbid starting inside a word or a longer number and ending
before another digit.

| Accepted | Rejected |
|---|---|
| `+57 3101234567`, `+57 310 123 4567` | `2018-08 - 2022-05` (dates) |
| `+1 212 555 0134`, `+1 (212) 555-0134` | `Room 101` |
| `3101234567`, `310-123-4567` | `(212) 555-0134` (a local number in parentheses) |

Every match is accepted by the `PHONE` terminal of the DSL, so the extracted
number can be written in the candidate document unchanged.

### LinkedIn — `LINKEDIN`

```python
LINKEDIN = r"https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?"
```

**Language.** `http` or `https`, `://`, an optional `www.`, `linkedin.com/in/`,
a profile identifier (letters, digits, `_`, `-`) and an optional final `/`.

## 3. Skills

One pattern per category. Each one is a union of **finite** languages, so the
language of each category is finite, hence regular. With `re.IGNORECASE` every
string below is also accepted in any letter case (`JS`, `Js`, `js`, …), and
`␣` stands for a space or a tab.

| Category | Pattern | Strings it recognizes |
|---|---|---|
| Programming languages | `java[ \t]?script\|type[ \t]?script\|python3?\|scala\|css3?\|(?<!\.)js\|(?<!\.)ts` | javascript, java␣script, typescript, type␣script, python, python3, scala, css, css3, js, ts |
| Frameworks and libraries | `react(?:[ \t.]?js)?\|angular(?:[ \t.]?js)?\|vue(?:[ \t.]?js)?\|node(?:[ \t.]?js)?\|django\|spring[ \t-]?boot\|tailwind(?:[ \t]?css)?\|pandas\|num[ \t]?py\|sklearn\|scikit[ \t-]?learn\|tensor[ \t]?flow\|py[ \t]?torch` | react, reactjs, react.js, react␣js (also for angular, vue and node), django, springboot, spring␣boot, spring-boot, tailwind, tailwindcss, tailwind␣css, pandas, numpy, num␣py, sklearn, scikitlearn, scikit␣learn, scikit-learn, tensorflow, tensor␣flow, pytorch, py␣torch |
| Databases | `postgres(?:ql)?\|mongo(?:[ \t]?db)?\|sql` | postgres, postgresql, mongo, mongodb, mongo␣db, sql |
| Tools and technologies | `git\|(?:apache[ \t])?spark\|pyspark\|(?:apache[ \t])?airflow\|docker\|kubernetes\|aws\|gcp\|terraform` | git, spark, apache␣spark, pyspark, airflow, apache␣airflow, docker, kubernetes, aws, gcp, terraform |

`SKILLS` is the union of the four languages, with a named group per category:

```python
SKILLS = (rf"\b(?:(?P<programming_languages>{PROGRAMMING_LANGUAGES})"
          rf"|(?P<frameworks_libraries>{FRAMEWORKS_LIBRARIES})"
          rf"|(?P<databases>{DATABASES})"
          rf"|(?P<tools>{TOOLS}))\b")
```

`SKILLS.finditer(text)` scans the text **once, left to right, without
overlapping matches**, and `match.lastgroup` names the category of each match.
This is what keeps `Node.js` as one framework instead of reading its `js` as a
language: the scan consumes `Node.js` before it reaches `js`. The word
boundaries `\b` keep `PostgreSQL` from producing `SQL`, and reject `GitHub`,
`MySQL` and `NoSQL`. The lookbehind `(?<!\.)` before `js` and `ts` rejects file
extensions such as `Next.js` or `app.ts`.

Example — the reference fragment of the assignment:

```
Wednesday Addams
3 years of experience developing web applications.
Technical Skills:
JS, React.js, NodeJS, Postgres, Git.
```

produces `JS`, `React.js`, `NodeJS`, `Postgres`, `Git`, the strings the
assignment expects from stage 1, in the order of the résumé.

### Unrecognized items of the skills list — `SKILLS_LIST`

```python
SKILLS_LIST = r"^[ \t]*(?:technical[ \t]+)?skills[ \t]*:[ \t]*\n?[ \t]*(?P<items>[^\n]+)"
LIST_SEPARATOR = r"[ \t]*[,;][ \t]*"
```

**Language.** A line that starts with `Skills:` or `Technical Skills:`, followed
by the list on the same line or on the next one. The list is split at commas
or semicolons; an item that is not, as a whole, a string of `SKILLS` (for
example `COBOL`) is kept in `skills.unrecognized`, and stage 2 reports it as
unknown instead of losing it.

## 4. Other qualifications — `OTHER_QUALIFICATIONS`

```python
OTHER_QUALIFICATIONS = (r"\b(?:rest(?:ful)?[ \t]+apis?|(?:predictive|machine[ \t-]learning)[ \t]+models?"
                        r"|data[ \t-]processing[ \t]+pipelines?|web[ \t]+applications?)\b")
```

**Language.** Descriptive phrases that are qualifications but not tools:
REST or RESTful API(s), predictive or machine-learning model(s), data-processing
pipeline(s), web application(s). They are reported, not normalized: no profile
automaton requires them.

## 5. Academic qualifications and education

### Degree keywords — `ACADEMIC`

```python
ACADEMIC = (r"\b(?:B\.?[ \t]?Sc\.?|M\.?[ \t]?Sc\.?|Ph\.?[ \t]?D\.?|Bachelor(?:'s)?|Master(?:'s)?"
            r"|Specialization|Diploma|Systems Engineering|Computer Science|Engineering|Ingenier[íi]a)"
            r"(?![A-Za-z])")
```

**Language.** Degree levels (`B.Sc.`, `BSc`, `M.Sc.`, `Ph.D.`, `Bachelor`,
`Master's`, `Specialization`, `Diploma`) and fields (`Computer Science`,
`Systems Engineering`, `Engineering`, `Ingeniería`). The lookahead `(?![A-Za-z])`
replaces a final `\b`, which would fail after the dot of `B.Sc.`.

### Education entries — `ENTRY` in the `Education:` section

```python
DATE = r"\d{4}-(?:0[1-9]|1[0-2])(?:-(?:0[1-9]|[12]\d|3[01]))?"
ENTRY = (rf"^[ \t]*(?P<title>[^\n]+?)[ \t]+at[ \t]+(?P<organization>[^\n(]+?)[ \t]*"
         rf"\((?P<start>{DATE})[ \t]*[-–][ \t]*(?P<end>{DATE}|present)\)[ \t]*$")
```

**Language.** Lines `Title at Organization (start - end)`. `DATE` is the same
language as the `DATE` terminal of the DSL: `YYYY-MM` or `YYYY-MM-DD` with a month
from 01 to 12 and a day from 01 to 31; the end may also be `present`. Example:
`B.Sc. in Computer Science at Empire State University (2019-08 - 2023-05)`.

`SECTION` splits the résumé at the headers `Technical Skills:`, `Skills:`,
`Languages:`, `Experience:` and `Education:` (each on a line of its own), so the
entries are read only inside their section.

## 6. Professional experience

### Years of experience — `YEARS`

```python
YEARS = r"\b(?P<years>\d{1,2})\+?[ \t]+(?:years?|años?|anos?)[ \t]+(?:of|de)[ \t]+(?:experience|experiencia)\b"
```

**Language.** A one- or two-digit number, an optional `+`, and "year(s) of
experience" in English or "año(s) de experiencia" in Spanish. Examples:
`3 years of experience`, `10+ years of experience`, `3 años de experiencia`;
`Graduated 4 years ago` is rejected.

### Positions and tasks — `ENTRY` and `TASK` in the `Experience:` section

```python
TASK = r"^[ \t]*[-•*][ \t]+(?P<task>[^\n]+?)[ \t]*$"
```

Positions use the same `ENTRY` pattern as degrees. The lines that start with
`-`, `•` or `*` between one position and the next are its tasks.

```
Investigative Software Developer at Nevermore Academy (2022-08 - present)
- Developed data analysis tools to investigate unusual events around Nevermore.
```

## 7. Spoken languages — `LANGUAGE` in the `Languages:` section

```python
LANGUAGE = (r"^[ \t]*(?P<name>[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)[ \t]*(?::|-|–|\()[ \t]*"
            r"(?P<level>native|full[ _]professional|professional|basic)\)?[ \t]*$")
```

**Language.** A language name, a separator (`:`, `-`, `–` or `(`) and a level
of the DSL scale. Examples: `English: native`, `Spanish (full professional)`.
The level is written as the DSL keyword (`full_professional`).

---

## Output data structure

`extract_resume_entities(text)` returns a dictionary grouped by type of
information, and `save_extracted_data(data, path)` stores it as JSON
(`python src/pipeline.py` writes it to `output/pipeline/<name>.json`). For
[`data/resumes/wednesday.txt`](../data/resumes/wednesday.txt), abridged:

```json
{
    "personal": {"name": "Wednesday Addams", "headline": "Full Stack Developer",
                 "location": "Jericho, Vermont", "summary": "Investigative software developer with a taste for the macabre."},
    "contact": {"email": "wednesday@nevermore.edu", "phone": null,
                "linkedin": "https://linkedin.com/in/wednesday-addams"},
    "skills": {"programming_languages": ["JS"], "frameworks_libraries": ["React.js", "NodeJS", "React"],
               "databases": ["Postgres"], "tools": ["Git"], "unrecognized": []},
    "technologies": ["JS", "React.js", "NodeJS", "Postgres", "Git", "React"],
    "other_qualifications": ["web applications", "REST APIs"],
    "academic_qualifications": ["Specialization"],
    "experience_years": 3,
    "experience": [{"title": "Investigative Software Developer", "organization": "Nevermore Academy",
                    "start": "2022-08", "end": "present", "tasks": ["Developed data analysis tools …", "Built REST APIs …"]}],
    "education": [{"title": "Specialization in supernatural investigations", "organization": "Nevermore Academy",
                   "start": "2018-08", "end": "2022-05"}],
    "languages": []
}
```

## Limitations

- **The whole text is scanned for skills.** A technology mentioned only in a
  task (`a React front end`) counts as a skill. Duplicates are removed, keeping
  the first occurrence.
- **The vocabulary is closed.** A technology outside the patterns (`MySQL`,
  `Express`) is not extracted, unless it is an item of the skills list, where it
  is kept as unrecognized.
- **Layout conventions.** The name must be the first line, positions and
  degrees must follow `Title at Organization (start - end)`, and a title that
  contains ` at ` is cut at its first ` at `.
- **Names.** Words must start with a capital letter; lowercase particles are
  limited to the listed ones.
