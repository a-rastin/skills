# Design basis

Adapted from the user's supplied “LLM Wiki: A pattern for building personal knowledge bases using LLMs.”

The central artifact is a maintained wiki, not a collection of documents retrieved afresh for each question. Keep three layers: immutable raw sources, an evolving linked wiki, and an explicit schema that teaches future sessions how to maintain it.

Ingestion compiles new evidence into source notes, entity/concept pages, and the existing synthesis. Queries can become durable, cited pages. Lint finds structural problems, stale conclusions, contradictions, and research opportunities. A categorized index supports navigation; an append-only log records evolution.

The user curates sources and directs exploration. The agent handles integration and bookkeeping. Obsidian provides a familiar reading and graph-navigation surface. Optional plugins, search engines, Git, visualizations, and publishing are extensions, not prerequisites.
