# kiarina-python Overview

kiari is built on [kiarina-python](https://github.com/kiarina/kiarina-python), a collection
of general-purpose libraries for building LLM agents.

- Local checkout: `~/src/github.com/kiarina/kiarina-python`; source code is canonical
- Package layout: a uv workspace under `packages/` using the `kiarina.*` namespace

This document is a reverse lookup for deciding which package to inspect. Package READMEs,
source, and tests remain canonical for detailed behavior.

> **Version drift:** Compare this document's [Documented Versions](#documented-versions)
> with kiari's `uv.lock`. If they differ, follow the
> [docs sync playbook](../../playbooks/kiarina-python-docs-sync.md).

## Package Layers

| Prefix | Role |
| --- | --- |
| `kiarina-agi-*` | Agent core under `kiarina.agi.*` |
| `kiarina-lib-*` | External-service clients under `kiarina.lib.*` |
| `kiarina-utils-*` | Common, file, and application utilities under `kiarina.utils.*` |
| Other | `kiarina-i18n`, `kiarina-currency`, and the `kiarina` meta package |

## Reverse Lookup: Goal to Package

### Agent Execution

See [Agent and Runner](agent-and-runner.md).

| Goal | Package / module |
| --- | --- |
| Define or run an agent | `kiarina-agi-runner` → `kiarina.agi.agent` |
| Run work as a task | `kiarina-agi-runner` → `kiarina.agi.task_runner` |
| Generate structured output | `kiarina-agi-runner` → `kiarina.agi.structured_output` |

### Workflows and Prompts

See [Workflow and Prompt](workflow-and-prompt.md).

| Goal | Package / module |
| --- | --- |
| Compose multi-step workflows | `kiarina-agi-flow` → `kiarina.agi.workflow` |
| Define one LLM prompt call | `kiarina-agi-flow` → `kiarina.agi.prompt` |
| Compose and weight prompt sections | `kiarina-agi-flow` → `section`, `section_container` |
| Manage state transitions | `kiarina-agi-flow` → `state`, `state_machine` |

### Tools

See [Tools](tools.md).

| Goal | Package / module |
| --- | --- |
| Define, register, and run tools | `kiarina-agi-tool` → `kiarina.agi.tool` |
| Run pre- and post-tool hooks | `kiarina-agi-tool` → `pre_hook`, `post_hook` |
| Log tool execution | `kiarina-agi-tool` → `tool_logger` |
| Adapt LangChain tools | `kiarina-agi-tool` → `langchain_tool` |

### Foundation and Data

See [Foundation](foundation.md).

| Goal | Package / module |
| --- | --- |
| Runtime identity and timezone | `kiarina-agi-base` → `run_context` |
| Cost, request, and token observation | `kiarina-agi-base` |
| Message, event, content, history, file, and tool data | `kiarina-agi-data` |
| Understand data ownership and persistence | [Data Model and History](data-model-and-history.md) |
| Build files and apply runtime policies | [FileInfo and Data Builder](file-info-and-data-builder.md) |
| Construct agent data | `kiarina-agi-data-builder` |
| Configure chat models and text embeddings | `kiarina-agi-text` |
| Store and cache files | `kiarina-agi-file` |

### Modality Providers

Audio, image, and video packages pair model abstractions with provider implementations.

| Modality | Package | Main capabilities |
| --- | --- | --- |
| Audio | `kiarina-agi-audio` | ASR, TTS, VAD, speaker changes, tagging, embeddings |
| Image | `kiarina-agi-image` | Generation, detection, segmentation, OCR, embeddings |
| Video | `kiarina-agi-video` | Generation and video sources |

### Infrastructure and Utilities

| Goal | Package |
| --- | --- |
| External-service configuration and clients | matching `kiarina-lib-*` package |
| Component registries and SettingsManager | `kiarina-utils-common` |
| File I/O, encoding, and MIME detection | `kiarina-utils-file` |
| Startup, user directories, and single-instance control | `kiarina-utils-app` |
| Translation catalogs | `kiarina-i18n` |
| Currency conversion for cost display | `kiarina-currency` |

## Common Pattern: Registry + Settings + Implementation

Most component families use the same structure:

- Define implementations with `Base<Name>` and a `@<name>` decorator.
- Register names in `<name>_registry` and resolve a name or import path specifier.
- Configure defaults, presets, and custom implementations with `<Name>Settings` and
  `settings_manager`.
- Keep built-in implementations in an adjacent `<name>_impl/` package.

A runtime-checkable protocol may be used as `ComponentRegistry.expected_type` when it
supports `isinstance` validation.

See [Runtime, Configuration, and Extensibility](../runtime-configuration-and-extensibility.md)
for how kiari applies this pattern.

## Documented Versions

These versions correspond to the kiari `uv.lock` reviewed for this documentation.

| Package | Documented version |
| --- | --- |
| kiarina (meta) | 2.27.0 |
| kiarina-agi-audio | 2.15.0 |
| kiarina-agi-base | 2.7.0 |
| kiarina-agi-data | 2.19.0 |
| kiarina-agi-data-builder | 2.21.1 |
| kiarina-agi-file | 2.21.3 |
| kiarina-agi-flow | 2.11.0 |
| kiarina-agi-image | 2.21.1 |
| kiarina-agi-runner | 2.21.0 |
| kiarina-agi-text | 2.22.1 |
| kiarina-agi-tool | 2.22.0 |
| kiarina-agi-video | 2.15.0 |
| kiarina-currency | 2.3.1 |
| kiarina-i18n | 2.3.1 |
| kiarina-lib-anthropic | 2.3.1 |
| kiarina-lib-cloudflare | 2.3.1 |
| kiarina-lib-cloudflare-d1 | 2.3.1 |
| kiarina-lib-falkordb | 2.3.1 |
| kiarina-lib-firebase | 2.27.0 |
| kiarina-lib-firebase-firestore | 2.27.0 |
| kiarina-lib-firebase-rtdb | 2.27.0 |
| kiarina-lib-google | 2.8.0 |
| kiarina-lib-openai | 2.3.1 |
| kiarina-lib-redis | 2.3.1 |
| kiarina-lib-redisearch | 2.17.0 |
| kiarina-lib-slack | 2.3.1 |
| kiarina-utils-app | 2.4.0 |
| kiarina-utils-common | 2.18.0 |
| kiarina-utils-file | 2.17.0 |
