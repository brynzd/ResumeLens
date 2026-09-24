"""Parse résumé specifications written in the ResumeLens DSL.

Loads the textX metamodel from ``grammar/resume.tx`` and builds the model of a
``.resume`` file, reporting lexical or syntactic errors when the file does not
conform to the grammar.

Usage:
    python src/parser.py examples/resume_01.resume
"""
