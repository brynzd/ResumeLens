# Generative AI Usage Log

The assignment allows level 3 use of generative AI (*colaboración con IAG*) and asks
for a record of the interactions with the content of our own authorship given to the
AI and the prompts used. This log records them per member. Prompts are quoted
verbatim, in the language they were written (Spanish); a local file path is replaced
by a placeholder.

Tool: **Claude Code** (Anthropic), run in the repository folder. The commits it wrote
were made under the member's own name, at the member's request, and are listed here.

## Bryan Moreno Diaz

### Session 1 — 2026-09-24: repository structure and first grammar

**Own content given to the AI:** the repository; Bryan's first EBNF draft of the
candidate profile grammar; the two assignment PDFs (`docs/assignment/`).

**Prompts:**

1. "Revisa todo el proyecto. Como primera tarea solo hay que dejar la estructura del proyecto como la que se sugiere en el documento @TextX_2026-2_CyED3.pdf"
2. "Necesito realizar la parte de la gramatica, como trabajaria de forma ordenada entre los archivos grammar, resume y metamodel? incluye mas archivos?"
3. "okey hago un primer borrador, ahora que?"
4. "usa las que están en @docs/assignment/Integrative-Task1-2026-2_CyED3.pdf que son 2"
5. "pero entonces de esa forma que lo habia escrito anteriormente, no tiene que ir en grammar.md? o simplemente lo tenia que haber puesto directamente en formato tx en el proyecto"
6. "haz los 2 puntos y agregar los dos resumes correspondientes que estaban en el enunciado"
7. "como puedo resumir esta sesion y usarla para otra sesion que vaya a abrir?"

**What the AI produced:** the folder structure suggested by the activity; an order of
work between the grammar, the examples and the metamodel; the translation of the EBNF
draft into textX syntax (match rules for `EMAIL`, `PHONE`, `URL`, `DATE`, `CANON`);
the two reference résumés of the assignment (Wednesday Addams, Mary Jane Watson)
written in the DSL.

**What we kept, changed and verified:** the EBNF draft stayed as the formal
specification in `docs/grammar.md`, with the textX grammar as its implementation.
Parsing the examples showed that textX needs an explicit `Comment` rule to ignore
`//` comments, which was added. Related commits: `5819858` (structure), `2edec85`
(résumés of the assignment), `3b1b7f4` (grammar in textX syntax).

### Session 2 — 2026-10-04: validation of the DSL

**Own content given to the AI:** the repository; two photos of the whiteboard with the
tasks the professor assigned for the activity.

**Prompts:**

1. "Chat estoy realizando mi tarea integradora en este proyecto sobre gramaticas y todo lo que he visto de Discretas 3. Necesito que revises el enunciado y todo el proyecto, porque necesito que me digas como agrego la parte de "validaciones". Pero antes de nada, necesito que me explique todo el flujo de como se tiene que trabajar este proyecto, con corde a los temas vistos. Necesito que me vuelvas a explicar de forma guiada los temas que hemos visto en discretas y como se conectan cada uno, para a su vez resolver un proyecto como este, ya que olvide casi por completo el temario y por consiguiente no se como seguir trabajando mi proyecto."
2. "A" (answer to a question of the AI: run the proposed checks on a temporary copy of the project).
3. "realiza solo lo de validaciones [Image #1] [Image #2]. No hemos hecho otras cosas porque solo hacemos lo que la profesora nos coloco en el tablero (en las imagenes). Realiza los commits necesarios en esta misma rama develop, pero sin tu etiqueta en los commits, de modo que sea yo el que pushee"

**What the AI produced:** a guided explanation of the course topics and how they connect
in the project; the validation of the DSL: valid and invalid specifications in `tests/`,
the restriction of `DATE` to existing months and days, the semantic checks of
`src/validator.py`, and Markdown generated only for valid résumés.

**What we verified:** the validation suite behaved as expected, first on a temporary
copy and then in the repository (`python src/validator.py`: 30 of 30 specifications,
25 of them invalid). Commits:
`3b75958`, `59200b5`, `e965825`, `eae80bf`, pushed by Bryan.

### Session 3 — 2026-10-11 to 2026-10-13: study guide, review and completion

**Own content given to the AI:** Bryan's class notes of the course (Obsidian, sessions 1
to 9); the repository, including the stages 1-3, the Streamlit app and the poster the
team wrote on 2026-10-10 and 2026-10-11; the assignment PDFs; the answer to a question
of the AI (the IDE used by the team: Visual Studio Code).

**Prompts:**

1. 2026-10-11: "Este trabajo es sobre mi curso de computacion y estructuras discretas 3. Los apuntes de lo que hemos visto está en [ruta local de los apuntes en Obsidian] y necesito que veas lo que hemos visto, faltan varios temas pero es para que tengas como guía. Estamos realizando el pryecto final que aplica todos los conceptos que hemos visto, y hemos resuelto varias cosas, sin embargo perdi la linea de todo y necesito varias cosas. 1. Entender todos los conceptos que se aplican en el proyecto, 2. ver de que trata el proyecto y su enunciado, 3. como aplican los conceptos en el proyecto, 4. realizar las etapas de lo que se tiene que realizar en el proyecto, 5. revisar que tiene el proyecto y decirme de que trata cada cosa que hasta ahora esta hecho 6. ver que falta para terminarlo el dia de hoy. todo esto lo agregar en formato .md en una carpeta, que no se subirá al git (.gitignore)."
2. 2026-10-12: "Realiza un documento explicando unicamente los conceptos que se aplican al proyecto. Definicion, que es, de que trata y ya. Algo sencillo. Despues explica mas detalladamente el pipeline del proyecto, no expliques documentos solo proceso"
3. 2026-10-13: "Acorde a todo lo que se menciono en el conceptos y pipeline 07, Revisa el proyecto y dime que falta por realizar o si ya todo queda funcionando correctamente, solo realiza ese analisis y listame si esta en orden todo, siguiendo tambien las indicaciones del enunciado oficial y que todo este correctamente documentado y programado, no realizar cambios todavia"
4. 2026-10-13: "Ignora lo de las invitaciones. Realiza lo que falta, las correciones, inconsistencias y errores en el codigo y documentacion. No toque aun el poster. Full stack acepta SQL. Todo esto agregalo en diferentes commits para main, sin tu etiqueta de claude, deja los commits unicamente listos"

**What the AI produced:**

- A personal study guide of the concepts and the pipeline, with a proposal of code for
  stages 1 to 3 that the team did not adopt (not part of the repository; its sample
  résumés were reused in `data/resumes/`).
- A review of the delivered project against the two assignment documents: what worked,
  what was missing and which results were wrong (for example the phone "+57 ", the
  missing TensorFlow and the Data Engineer verdict of `resume_02`).
- The commits of 2026-10-13, from `build: run the test suite with pytest and support
  Python 3.14` to `docs: rewrite the README for the whole project`: the corrections of
  stages 1 to 3, SQL in the Full Stack profile, the classification against the four
  profiles, the generation of the candidate document from a résumé, the Streamlit UI of
  the four stages, `resume_03`, the diagrams, the verdict check of the validator, the
  tests, and the documents `regular_expressions.md`, `transducers.md`,
  `normal_forms.md`, `design.md`, `test_cases.md`, `literature_review.md`, this log and
  the README.

**What we verified:** `python -m pytest` (278 tests), `python src/validator.py` (32 of 32
specifications as expected), `python src/pipeline.py data/resumes/*.txt` (the seven
sample résumés), the UI with `streamlit.testing`, and the installation of
`requirements.txt` with Python 3.12. Bryan reviews these commits before pushing them.

## Other members

Each member adds here, with the same structure, the interactions they had with
generative AI tools for the project (date, tool, own content given, prompts, what was
used, what was changed and verified).
