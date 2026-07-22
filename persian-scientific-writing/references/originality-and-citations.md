# Originality and Citations Workflow

Apply this workflow to every Persian scientific writing request. The language constraints in steps 5 and 6 govern drafting in step 4 from its first sentence; the later steps verify compliance rather than trigger a wholesale rewrite.

## 1. Mine supplied source material

Treat every file attached to the writing request as potential source material, including PDFs, drafts, notes, datasets, slides, and code. Also treat a substantial pasted block as source material when the user explicitly labels it as such, for example `پاراگراف منبع:` or `چکیده منبع:`. Do not trigger mining for casual instructions, short working notes, or unlabeled fragments.

Inspect each source for claims, results, methods, definitions, limitations, and bibliographic metadata that could support the requested text. For datasets and code, distinguish what the artifact directly establishes from what would require analysis or an external publication. Never treat a filename, code comment, or unsupported note as scientific evidence.

## 2. Emit the candidate audit before prose

When the audit is visible, write it in Persian and place it before citation decisions and before the drafted prose. Give every candidate source these six fields:

1. **Source:** supplied filename or labeled pasted-block identifier.
2. **Reference metadata:** author, title, year, venue, DOI, citation key, or other supplied metadata; mark missing fields instead of guessing.
3. **Citable claim:** a faithful Persian statement of what the source supports.
4. **Evidence anchor:** exact page, slide, section, table, figure, line, cell, or other locator. Include an exact quotation only when the quotation rules below permit reproducing it; otherwise give the locator and a faithful Persian paraphrase.
5. **Confidence:** `بالا`, `متوسط`, or `پایین`, measuring how closely the source claim matches the assertion planned for that citation spot. Use `بالا` for a direct match, `متوسط` for a defensible but partial match, and `پایین` for indirect or ambiguous support.
6. **Alternatives:** supplied sources that could replace or supplement this source, with a brief reason; write `ندارد` when none was found.

Do not expose the candidate audit in these four cases:

1. The user explicitly requests only clean copy, no preface, or no analysis.
2. The task is limited to correction, proofreading, formatting, or translation and does not add or reconsider citations.
3. The request is a short local edit for which mining cannot affect the cited claims.
4. A candidate audit has already been shown and accepted for the same document, and neither the sources nor relevant claims have changed.

In these cases, mine silently when citation choices still matter, or skip mining when it cannot affect the work. Return only the requested prose or correction.

## 3. Decide what to cite

After the candidate audit, show a separate Persian citation plan. Mark each selected candidate, the exact claim or paragraph it will support, and whether it is primary support, supplementary support, or an alternative. Reject weak candidates explicitly when that prevents overclaiming. Then write the prose. Do not cite every mined source merely because it is available.

Apply these citation-distribution limits throughout the complete document:

  - Maximum repetition of one reference: Cite each unique reference no more than three times in the entire document. Count every separate citation location, whether the reference appears alone or inside a grouped citation. Before finalizing, audit citation frequency by citation key or other unique reference identifier. When a reference would otherwise appear a fourth time, consolidate nearby supported claims where academically appropriate or use another genuinely suitable source. Never substitute an irrelevant source merely to satisfy this limit.
Maximum references per argument: Use one or two of the strongest and most directly relevant references for most arguments. Use three to five different references only when the argument genuinely requires broader support, such as demonstrating consensus, representing conflicting findings, or documenting variation across populations or methods. Never cite more than five different references for a single argument, claim, or tightly connected reasoning unit. Avoid citation dumping.

  - Treat an argument as one factual claim, interpretive proposition, or tightly connected reasoning unit that the cited evidence is intended to support. Do not evade the five-reference limit by splitting one argument into artificial sentence fragments, and do not merge unrelated claims merely to reduce citation counts.

  - Before drafting and again before final delivery, verify both limits systematically: no unique reference appears at more than three citation locations in the whole document, and no argument is supported by more than five distinct references.

  - Preserve the boundary between prior work and the present study. Describe cited external authors in third person. Reserve ما for the present study's own supplied contribution and synthesis. A safe pattern is: رفیعی و همکاران نشان دادند که ...؛ ما با گسترش آزمون به نمونه‌ای بزرگ‌تر دریافتیم که ... Only write the second clause when the supplied study material establishes it.

## 4. Write as the author of the present study

Write the manuscript in an original authorial voice, as though composing the authors' own account of the supplied study. Do not mention being an AI, receiving files, or merely restating notes in the manuscript. Use `ما` as the sole default first-person form in solo-author theses, multi-author papers, proposals, and translations. If the user or supervisor explicitly requires a different pronoun or impersonal voice, honor that override consistently for the whole document rather than switching sentence by sentence.

Use `ما` only for contributions the supplied material attributes to the present study. Use past or present tense for work actually completed and future or prospective language for proposed work. Do not imply that the authors performed a method, obtained a result, or reached a conclusion absent from the sources.

Interpret supplied findings as a domain expert would: relate results to plausible mechanisms, identify trade-offs, reconcile or explain contrasts, and propose implications that follow from the evidence. Frame these as the authors' calibrated analysis with wording such as `ما این الگو را ناشی از ... می‌دانیم` or `از نظر ما، این یافته می‌تواند ... را نشان دهد`. Distinguish inference from observation and expose uncertainty. The author may later revise the interpretation; never fill an evidentiary gap with invented data.

Draft from the outset under the constraints in steps 5 and 6.

## 5. Verify that Persian prose contains no English typing or forbidden ASCII punctuation

Do not place ordinary English words or phrases inside Persian sentences. Terms such as `baseline`, `training`, `attention`, and `fine-tuning` must become Persian equivalents such as `خط پایه`, `آموزش`, `سازوکار توجه`, and `تنظیم دقیق` or an established Persian transliteration. If an established Persian equivalent exists, do not add the English term at first mention merely for decoration.

The following Latin-script material is protected only to the extent scientifically or mechanically necessary:

- an exact technical term at first mention when no adequate Persian equivalent exists and cross-language recognition is necessary;
- established gene, protein, species, chemical, model, instrument, and software names;
- standard units, equations, numbers, DOI strings, URLs, citation keys, bibliographic reference entries, and required citation callouts;
- exact inline-code identifiers enclosed in backticks, such as `print` or `forward()`;
- an English quotation explicitly tagged by the user as `[نقل قول انگلیسی]` or material explicitly tagged as `[کد]`.

Floating concept words are never code or nomenclature merely because they are typed in Latin script. For an untranslatable first-mention term, use a Persian description or transliteration followed by the Latin form in Persian guillemets, for example `نام تخصصی «Latin term؛ ABBR»`; then use only the chosen Persian form. This punctuation-safe form replaces round-parenthesis patterns because authored Persian prose must not contain ASCII `(`, comma `,`, or `)`.

Do not alter protected literals internally. Outside them, replace the ASCII comma with `،` and restructure round-parenthetical remarks using guillemets, dashes, commas, or a separate sentence. Preserve forbidden ASCII characters only when they are immutable parts of protected literals or venue-required citation syntax. Untagged English quotations are not protected: translate or paraphrase them into Persian with attribution.

Scan the final authored prose for Latin-script runs and for `(`, `,`, and `)`. Confirm that every remaining occurrence belongs to a protected literal; replace or restructure all others. Never use a carve-out to retain words such as `baseline` or `training` in a Persian sentence.

## 6. Verify that Persian prose contains no Arabic harakat or tashkil

Remove every combining mark whose Unicode script property is Arabic from Persian prose. This includes, but is not limited to, marks in U+0610–U+061A, U+064B–U+065F, U+0670, U+06D6–U+06ED, and U+08CA–U+08FF; treat the script-property rule as authoritative if later Unicode versions add marks elsewhere. This prohibition includes fathatan, dammatan, kasratan, fatha, damma, kasra, shadda, sukun, maddah as a combining mark, superscript alef, and Quranic annotation marks. Do not remove Persian letters such as `آ`, `أ`, or `ۀ` merely because their glyph contains a built-in mark; they are letters, not combining harakat.

The only exception is a verbatim Arabic quotation that the user explicitly labels inline as `[نقل قول عربی]` or `[منبع عربی]`. Preserve its harakat exactly. Arabic-looking text in an attachment or an untagged pasted block does not qualify automatically; cite it by anchor and use an undiacritized Persian paraphrase unless the user supplies the explicit tag.

Scan the final authored prose by Unicode character, not visual appearance. Remove every prohibited combining mark outside an explicitly tagged Arabic quotation, then recheck that the correction did not alter protected identifiers, equations, citation syntax, or meaning.
