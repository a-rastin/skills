# Examples

Every actual response produced by this skill must contain exactly one fenced `latex` block and no surrounding prose.

## 1. Plain English text

Input:

```text
Revenue increased by 15% in R&D.
```

Output:

```latex
Revenue increased by 15\% in R\&D.
```

## 2. Plain Persian text

Input:

```text
این مطالعه در سال ۱۴۰۲ انجام شد.
@persian
```

Output:

```latex
این مطالعه در سال ۱۴۰۲ انجام شد.
```

## 3. Percent replacement

Input:

```text
میزان پاسخ 82% بود.
@persian @percent
```

Output:

```latex
میزان پاسخ 82 درصد بود.
```

## 4. One paragraph

Input:

```text
This is the first sentence.

This is the second paragraph.
@onepar
```

Output:

```latex
This is the first sentence. This is the second paragraph.
```

## 5. Plain itemize

Input:

```text
@itemize
• Apple
• Orange
• Pear
```

Output:

```latex
\begin{itemize}
  \item Apple
  \item Orange
  \item Pear
\end{itemize}
```

## 6. Bold itemize

Input:

```text
@itemize
• **First item**
• **Second item**
```

Output:

```latex
\begin{itemize}
  \item \textbf{First item}
  \item \textbf{Second item}
\end{itemize}
```

## 7. Label-description itemize in Persian

Input:

```text
@persian @itemize
• سن: بر حسب سال ثبت شد.
• جنس: زن یا مرد ثبت شد.
```

Output:

```latex
\begin{itemize}
  \item \textbf{سن:} بر حسب سال ثبت شد.
  \item \textbf{جنس:} زن یا مرد ثبت شد.
\end{itemize}
```

## 8. Plain enumerate

Input:

```text
@enumerate
1. Collect data.
2. Analyze data.
3. Report results.
```

Output:

```latex
\begin{enumerate}
  \item Collect data.
  \item Analyze data.
  \item Report results.
\end{enumerate}
```

## 9. Label-description enumerate

Input:

```text
@enumerate
1. Input: Read the source text.
2. Conversion: Preserve its meaning.
3. Output: Return LaTeX code.
```

Output:

```latex
\begin{enumerate}
  \item \textbf{Input:} Read the source text.
  \item \textbf{Conversion:} Preserve its meaning.
  \item \textbf{Output:} Return LaTeX code.
\end{enumerate}
```

## 10. Mixed Persian and English

Input:

```text
@persian
فایل chapter_1.tex با XeLaTeX کامپایل شد.
```

Output:

```latex
فایل \lr{chapter\_1.tex} با \lr{XeLaTeX} کامپایل شد.
```

## 11. Explicit headings

Input:

```text
# Introduction
## Background
The study included 120 participants.
```

Output:

```latex
\section{Introduction}
\subsection{Background}
The study included 120 participants.
```

## 12. Standalone mathematics

Input:

```text
y = mx + c
```

Output:

```latex
\[
y = mx + c
\]
```

Only use this conversion when the line is unmistakably a mathematical expression.

## 13. Existing citation text

Input:

```text
Previous work reported similar findings [12].
```

Output:

```latex
Previous work reported similar findings [12].
```

Do not invent a citation key.

## 14. Conflicting list commands

Input:

```text
@itemize @enumerate
• One
• Two
```

Output:

```latex
% ERROR: @itemize and @enumerate cannot be used together.
```

## 15. Command list

Input:

```text
@commandlist
```

Output:

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
