# Requeriments

- FR-01 The system shall accept a résumé as plain text (file or pasted text).

- FR-02 The system shall support four profiles: Full Stack Developer, Machine Learning Engineer, Front-end Engineer and Data engineer.

- FR-03 The system shall process all four profiles through a single general pipeline, with each profile defined as data (normalization rules, canonical order, automaton) rather than as a separate implementation.

- FR-04 The system shall run every résumé through the complete pipeline before reporting any profile result.

- FR-05 The system shall extract, using regular expressions implemented with Python's re module: contact information, programming languages, frameworks and libraries, databases, academic qualifications, professional experience, tools and technologies, and other profile-relevant qualifications.

- FR-06 The system shall extract multi-word and punctuated variants (e.g., "scikit learn", "Tensor Flow", "React.js") as single items. 

- FR-07 The system shall extract years of experience and descriptive phrases that map to non-tool qualifications (e.g., machine-learning model development).

- FR-08 The extraction stage shall output raw strings exactly as written, without resolving equivalences or evaluating profiles.

- FR-09 The system shall store extracted information, grouped by category, in a file or data structure.

- FR-10 The system shall transform each extracted string into its canonical token using finite-state transducers implemented with pyformlang.

- FR-11 The transducers shall cover team-proposed variants (case, abbreviations, separators, suffixes such as ".js") beyond the assignment's examples.

- FR-12 The system shall handle strings not recognized by any transducer in a defined way (discard or tag as unknown) without failing.

- FR-13 The system shall remove duplicate canonical tokens produced by different variants of the same qualification.

- FR-14 The system shall sort normalized tokens according to each profile's canonical order before recognition.

- FR-15 For each profile, the system shall evaluate the sorted sequence with that profile's finite automaton (DFA, NFA or ε-NFA) implemented with pyformlang and output ACCEPTED or REJECTED.

- FR-16 The system shall report every profile whose automaton accepts, allowing zero, one, or multiple accepted profiles per résumé.

- FR-17 The system shall not rank candidates or issue hiring decisions.

- FR-18 The system shall generate a candidate-profile document in the team's DSL containing personal information, contact information, one or more experience entries, one or more education entries, normalized skills, and the result for each accepted profile.

- FR-19 The system shall parse and validate DSL documents with a textX grammar.

- FR-20 The system shall reject DSL documents that violate lexical or syntactic rules and display an error message.

- FR-21 The system shall accept DSL documents loaded from external files, not only self-generated ones.

- FR-22 The system shall generate a short HTML or Markdown visualization from each validated DSL document.

- FR-23 The system shall provide a UI to load a résumé, run the pipeline, and display each stage's output: extracted strings, normalized tokens, sorted sequence, per-profile result, DSL document, and visualization.

FR-24 The system shall include automated tests for each stage, covering the two reference résumés, positive and negative cases per profile, and invalid DSL documents.