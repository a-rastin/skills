# Command Reference

## General parsing rules

- A recognized command is a standalone token beginning with `@`.
- Recognized commands may appear at the beginning, end, or between lines of the input.
- Remove recognized command tokens before converting content.
- Multiple instances of the same command have the same effect as one instance.
- Do not interpret a command name inside a code sample, quoted literal, email address, or URL as a control token when it is clearly literal.
- Unknown `@tokens` are ordinary content and must not trigger behavior.

## Precedence

Apply commands in this order:

1. `@commandlist`
2. conflict detection for `@itemize` and `@enumerate`
3. `@persian`
4. `@percent`
5. `@itemize` or `@enumerate`
6. `@onepar`
7. normal escaping and output validation

### Precedence consequences

- If `@commandlist` is present, return only the command list. Ignore all other content and commands.
- `@itemize` and `@enumerate` are mutually exclusive. If both occur, return only this code inside the required fence:

```latex
% ERROR: @itemize and @enumerate cannot be used together.
```

- If `@onepar` occurs with a list command, it joins wrapped lines **within each list item** and joins non-list prose into one paragraph; it does not flatten the list environment into a paragraph.
- `@percent` acts on literal percent signs in user content before LaTeX escaping. It does not alter percent signs generated internally in an error comment.

## `@commandlist`

### Function

Return the list and function of all supported commands as LaTeX-ready code.

### Output

Use this exact structural form:

```latex
\begin{description}
  \item[\texttt{@commandlist}] Displays the list and function of all supported commands.
  \item[\texttt{@onepar}] Joins all prose sentences and paragraphs into one paragraph; inside a requested list, joins wrapped lines within each item without removing the list.
  \item[\texttt{@persian}] Treats the input as Persian and applies XeLaTeX/xepersian-compatible direction and Unicode rules.
  \item[\texttt{@percent}] Replaces every literal \% sign in the input content with the Persian word «درصد».
  \item[\texttt{@itemize}] Converts the supplied bullet list into an \texttt{itemize} environment using the matching list template.
  \item[\texttt{@enumerate}] Converts the supplied numbered list into an \texttt{enumerate} environment using the matching list template.
\end{description}
```

When the surrounding request is clearly Persian, the descriptions may be written in Persian, but command names and behavior must remain unchanged.

## `@onepar`

### Function

Join all prose into a single paragraph.

### Rules

- Replace paragraph breaks and soft line breaks with one ordinary space.
- Preserve sentence punctuation.
- Collapse repeated whitespace to one space, except protected spaces inside existing valid LaTeX or verbatim-like content.
- Do not add or remove sentences.
- Do not insert `\\`.
- If list conversion is also requested, retain the list and join only wrapped lines belonging to each item.
- Preserve display mathematics as a block; do not force a display equation onto the same source line merely to satisfy `@onepar`.

## `@persian`

### Function

Mark the input as Persian and apply XeLaTeX/xepersian-compatible conversion rules.

### Rules

- Remove the token from output.
- Preserve Persian Unicode characters and نیم‌فاصله.
- Do not transliterate or translate.
- Do not add a full preamble.
- Use `\lr{...}` only where needed for a coherent embedded left-to-right run.
- Preserve the supplied digit style.

## `@percent`

### Function

Replace every literal `%` in user content with the Persian word `درصد`.

### Rules

- Replacement is textual, not mathematical.
- Insert normal spacing so the result is readable:
  - `25%` → `25 درصد`
  - `% 25` → `درصد 25`
- Do not replace the word `percent`, `percentage`, or `درصد`; only replace the `%` character.
- Do not escape the replaced sign as `\%` because the sign no longer exists.
- When `@percent` is absent, literal `%` becomes `\%` in text mode.

## `@itemize`

### Function

Convert a bullet list into `itemize`.

Recognize common bullet markers at the start of a line, including `•`, `-`, `–`, `—`, and `*`, only when they function as list markers.

### Possibility 1: plain items

Input pattern:

```text
• sometext1
• sometext2
• sometext3
```

Output template:

```latex
\begin{itemize}
  \item sometext1
  \item sometext2
  \item sometext3
\end{itemize}
```

### Possibility 2: every item explicitly bold

Input pattern: every complete item is explicitly marked bold by source formatting, such as `**sometext1**`.

Output template:

```latex
\begin{itemize}
  \item \textbf{sometext1}
  \item \textbf{sometext2}
  \item \textbf{sometext3}
\end{itemize}
```

Do not infer bold from capitalization, short length, or visual importance.

### Possibility 3: label followed by description

Input pattern:

```text
• sometext1: sometext2.
• sometext3: sometext4.
• sometext5: sometext6.
```

Output template:

```latex
\begin{itemize}
  \item \textbf{sometext1:} sometext2.
  \item \textbf{sometext3:} sometext4.
  \item \textbf{sometext5:} sometext6.
\end{itemize}
```

Rules:

- Bold only the leading label and its colon.
- Split at the first clear label separator (`:` or Persian `：` if supplied).
- Do not use Possibility 3 for times, ratios, URLs, DOI strings, or other cases where the colon is not a label separator.
- Preserve punctuation after the description.

### Mixed formatting

If items have mixed explicit formatting, preserve formatting item by item. Do not force all items into Possibility 2.

## `@enumerate`

### Function

Convert a numbered list into `enumerate`.

Recognize list markers such as `1.`, `1)`, `۱.`, `۱)`, `(1)`, and `(۱)` at the beginning of lines. Remove source numbering and let LaTeX generate numbers.

### Possibility 1: plain items

```latex
\begin{enumerate}
  \item sometext1
  \item sometext2
  \item sometext3
\end{enumerate}
```

### Possibility 2: every item explicitly bold

```latex
\begin{enumerate}
  \item \textbf{sometext1}
  \item \textbf{sometext2}
  \item \textbf{sometext3}
\end{enumerate}
```

### Possibility 3: label followed by description

```latex
\begin{enumerate}
  \item \textbf{sometext1:} sometext2.
  \item \textbf{sometext3:} sometext4.
  \item \textbf{sometext5:} sometext6.
\end{enumerate}
```

Use the same bold-detection, label-separator, punctuation, and mixed-format rules as `@itemize`.
