# Acceptance Test Cases

A compliant model should produce the expected body code inside exactly one `latex` fence and no surrounding prose.

## Test 1: reserved characters

Input:

```text
A&B uses file_name #2 and costs $5 at 10%.
```

Expected body:

```latex
A\&B uses file\_name \#2 and costs \$5 at 10\%.
```

## Test 2: Persian percent command

Input:

```text
@persian @percent
پایبندی در 76% بیماران مشاهده شد.
```

Expected body:

```latex
پایبندی در 76 درصد بیماران مشاهده شد.
```

## Test 3: one paragraph without content loss

Input:

```text
@onepar
Sentence one.

Sentence two.
Sentence three.
```

Expected body:

```latex
Sentence one. Sentence two. Sentence three.
```

## Test 4: Persian plain bullet list

Input:

```text
@persian @itemize
• مورد اول
• مورد دوم
```

Expected body:

```latex
\begin{itemize}
  \item مورد اول
  \item مورد دوم
\end{itemize}
```

## Test 5: all-bold bullet list

Input:

```text
@itemize
• **Alpha**
• **Beta**
```

Expected body:

```latex
\begin{itemize}
  \item \textbf{Alpha}
  \item \textbf{Beta}
\end{itemize}
```

## Test 6: label-description bullet list

Input:

```text
@itemize
• Name: Ali.
• Age: 31.
```

Expected body:

```latex
\begin{itemize}
  \item \textbf{Name:} Ali.
  \item \textbf{Age:} 31.
\end{itemize}
```

## Test 7: Persian numbered list with Persian digits

Input:

```text
@persian @enumerate
۱. گردآوری داده‌ها
۲. تحلیل داده‌ها
```

Expected body:

```latex
\begin{enumerate}
  \item گردآوری داده‌ها
  \item تحلیل داده‌ها
\end{enumerate}
```

## Test 8: no invented citation key

Input:

```text
The result was significant [7].
```

Expected body:

```latex
The result was significant [7].
```

Forbidden output includes any invented `\cite{...}`.

## Test 9: mixed direction

Input:

```text
@persian
تحلیل با SPSS نسخه 29 انجام شد.
```

Expected body:

```latex
تحلیل با \lr{SPSS} نسخه 29 انجام شد.
```

## Test 10: conflict handling

Input:

```text
@itemize @enumerate
1. One
2. Two
```

Expected body:

```latex
% ERROR: @itemize and @enumerate cannot be used together.
```

## Test 11: command list precedence

Input:

```text
@commandlist @percent
Ignore this 20% text.
```

Expected: only the complete command-list `description` environment. The input sentence must not appear.

## Test 12: environment validation

For every generated list:

- `\begin{itemize}` must match `\end{itemize}`.
- `\begin{enumerate}` must match `\end{enumerate}`.
- Every `\item` must be inside a list environment.
- All braces must be balanced.
