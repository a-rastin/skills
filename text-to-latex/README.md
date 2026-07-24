# text-to-latex skill

A conservative LLM skill for converting Persian, English, or mixed plain text into LaTeX-ready body code.

## Main behavior

- Returns exactly one `latex` code block.
- Preserves content and does not answer or invent information.
- Escapes LaTeX-reserved characters.
- Supports XeLaTeX/xepersian conventions for Persian.
- Implements `@commandlist`, `@onepar`, `@persian`, `@percent`, `@itemize`, and `@enumerate`.

## Validation

Run:

```bash
python scripts/validate_skill.py
```
