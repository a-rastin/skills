# Templates

Replace placeholders with observed values; omit unknown fields and empty sections. Existing vault conventions take precedence. These are starting points, not mandatory sections on every page.

## Vault schema

```markdown
# Wiki maintenance

Scope: <domain and intended audience>
Vault root: <how the current workspace identifies this vault>
Raw sources: raw/ (immutable)
Generated pages: wiki/ (preserve user annotations)
Index: wiki/index.md
Activity log: wiki/log.md (append only)

Use vault-root-relative wikilinks and stable descriptive filenames.
Properties: type, created, updated, aliases, tags, sources.
Cite claims near their text and link source notes to originals.
Distinguish reported facts, inference, and unresolved contradictions.
Ingest: read source, check duplicates, summarize, integrate related pages,
update synthesis and index, verify, append log.
Query: consult index and evidence; save substantial new synthesis;
log saved queries only. Read-only requests change no files.
Lint: inspect links, provenance, contradictions, freshness, and connectivity;
repair only within the user's requested scope.
Keep raw files, user annotations, and unrelated settings intact.
```

## Source note

```markdown
---
type: source
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - source
---
# <Source title>

Original: [[raw/<file with extension>]]
Author / organization: <if known>
Published: <if known>
Original URL / accessed: <if web source>
Coverage: <complete or specific partial coverage>
Source identity: <path/URL and version; checksum if used>

## Summary
<Faithful concise account.>

## Evidence
<Key claims with real section/page/timestamp locators.>

## Limitations
<Source limitations and extraction gaps.>

## Connections
<Explain how this changes or supports linked topic pages.>
```

## Entity, concept, or derived answer

```markdown
---
type: concept
created: YYYY-MM-DD
updated: YYYY-MM-DD
aliases: []
tags: []
sources:
  - "[[wiki/sources/<Source title>]]"
---
# <Title>

<Current understanding with claim-level citations.>

## Evidence and interpretation
<Distinguish what sources say from synthesis.>

## Tensions and open questions
<Only when meaningful; cite both sides of disagreements.>

## Connections
<Relevant links with an explanation of the relationship.>
```

## Index entry

`- [[wiki/concepts/<Title>|<Title>]] — <one-line description>`

## Append-only log entry

```markdown
## [YYYY-MM-DD] ingest | <Source title>
- Source: [[wiki/sources/<Source title>]]
- Created: <links>
- Updated: <links and meaningful changes>
- Unresolved: <conflicts, gaps, or partial failures, if any>
```

Other operation labels: `query`, `lint`, `initialize`, `update`.

## Official syntax references

- [Obsidian internal links](https://help.obsidian.md/links): wikilinks, vault-relative folder paths, aliases, heading/block links, and attachment extensions.
- [Obsidian properties](https://help.obsidian.md/properties): YAML properties, quoted internal links, lists, and date values.

Syntax checked 2026-09-16. Consult current official help before introducing unfamiliar application features; avoid depending on version-specific UI controls.
