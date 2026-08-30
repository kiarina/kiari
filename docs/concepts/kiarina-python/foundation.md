# Foundation: Context, Data Model, Chat

The kiarina-agi-base, data, data-builder, file, and text packages provide the shared
foundation most frequently imported by kiari.

See [Documented Versions](overview.md#documented-versions) for the assumed versions.

## kiarina-agi-base: Runtime Context and Observability

| Module | Responsibility |
| --- | --- |
| `kiarina.agi.run_context` | `RunContext` and `RunContextSettings` for execution identity and timezone |
| `kiarina.agi.cost_recorder` | Cost aggregation contract and registry |
| `kiarina.agi.cost_logger` | Cost logging contract; kiari implementations are under `kiari/impl/cost_logger_impl/` |
| `kiarina.agi.cost_record`, `cost_utils` | Cost data and calculations |
| `kiarina.agi.request_logger` | LLM request logging contract |
| `kiarina.agi.token_utils` | Token estimation and counting |
| `kiarina.agi.console_utils` | Console presentation helpers |
| `kiarina.agi.file_utils`, `image_types` | File and image helper types |

## kiarina-agi-data: Data Model

This package owns the Pydantic models used by agents. Models contain closely related
operations such as serialization, estimation, and shrinking. Cross-model construction and
normalization belong to data-builder.

| Module | Responsibility |
| --- | --- |
| `kiarina.agi.message` | `Message`, `AIMessage`, `ToolMessage`, and related types |
| `kiarina.agi.history` | Conversation `History`; kiari owns persistence adapters |
| `kiarina.agi.event` | Streaming `Event` values emitted by agent runs |
| `kiarina.agi.content`, `display_content` | Provider content and display content |
| `kiarina.agi.file_info`, `file_info_pool`, `file_bundle` | Attachment metadata and alternatives |
| `kiarina.agi.tool_info` | Tool definition metadata |
| `kiarina.agi.chat_limits`, `chat_estimates` | Context limits and estimates |
| `kiarina.agi.embedding` | Embedding data types |

See [Data Model and History](data-model-and-history.md) for ownership, streaming,
persistence, and hydration boundaries.

`FileInfo` policy fields such as `pinned`, `inline`, `metadata_only`,
`content_only`, `no_merge`, `group`, `unique_key`, and `keep_from_end` affect
history, limit adjustment, and prompt conversion. See
[FileInfo and Data Builder](file-info-and-data-builder.md).

## kiarina-agi-data-builder: Data Construction

Builders for messages, histories, events, content, tools, and files convert execution-mode
input into agent history. Related capabilities include file factories, loaders, local
scanners, segment normalization, and file adjustment.

Use `rg 'file_info_loader|event_builder|local_scanner' kiari/` to find call sites.

With analysis enabled, PDF and video builders can produce capability-aware `FileBundle`
alternatives. PDFs may include native PDF, page images, and extracted text. Videos may
include native video, timestamped frames, transcripts, and ambient events. The default is
disabled; see [FileInfo and Data Builder](file-info-and-data-builder.md) for settings.

## kiarina-agi-file: Files, Caches, and Repositories

This package contains file abstractions, asset caches, asset repositories, and local
repositories used for attachments and generated artifacts.

## kiarina-agi-text: Chat and Text Embeddings

| Module | Responsibility |
| --- | --- |
| `kiarina.agi.chat_model`, `chat_provider` | Chat model and provider contracts, including `ChatOptions` |
| `kiarina.agi.langchain_chat_provider` | LangChain-backed Anthropic, OpenAI, Google, and other providers |
| `kiarina.agi.chat_logger` | Chat logging contract; kiari implementations are under `kiari/impl/chat_logger_impl/` |
| `kiarina.agi.text_embedding_model`, `text_embedding_provider` | Text embedding abstractions |

Provider cost records may distinguish tiered pricing and prompt-cache write costs. Cost
loggers and recorders must preserve the provider's full cost breakdown rather than assume
only input and output token totals.
