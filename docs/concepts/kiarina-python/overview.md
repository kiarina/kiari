# kiarina-python Overview

kiari は、AGI を目指す LLM エージェント構築のための汎用ライブラリ群
[kiarina-python](https://github.com/kiarina/kiarina-python) の上に作られています。

- ローカルパス: `~/src/github.com/kiarina/kiarina-python`（正典はコード）
- パッケージ実体: `packages/` 以下の uv workspace。名前空間は `kiarina.*`

この文書は「何をしたいときに、どのパッケージを調べるか」の逆引き地図です。
詳細仕様は各パッケージの README・ソース・テストを正典とし、ここには複製しません。

> **バージョンずれに注意**: kiarina-python は仕様が頻繁に変わります。この文書群は
> 文末の [Documented Versions](#documented-versions) 時点の記述です。kiari の `uv.lock` の
> バージョンと表がずれていたら、[kiarina-python docs sync playbook](../../playbooks/kiarina-python-docs-sync.md)
> に従って差分を確認し、文書を更新してください。

## Package Layers

| 接頭辞 | 役割 |
| --- | --- |
| `kiarina-agi-*` | LLM エージェント構築の中核。`kiarina.agi.*` 名前空間 |
| `kiarina-lib-*` | 外部サービスのクライアント（Anthropic, OpenAI, Google, Firebase, Redis, Cloudflare, Slack, FalkorDB, Atlassian）。`kiarina.lib.*` |
| `kiarina-utils-*` | 汎用ユーティリティ（common / file / app）。`kiarina.utils.*` |
| その他 | `kiarina-i18n`（国際化）、`kiarina-currency`（通貨・コスト換算）、`kiarina`（メタパッケージ） |

## 逆引き: やりたいこと → 調べるパッケージ

### エージェント実行まわり（詳細: [agent-and-runner.md](agent-and-runner.md)）

| やりたいこと | パッケージ / モジュール |
| --- | --- |
| Agent を定義・実行する（`run_agent` / `invoke_agent` / `stream_agent`） | `kiarina-agi-runner` → `kiarina.agi.agent` |
| バックグラウンドタスクとして実行する | `kiarina-agi-runner` → `kiarina.agi.task_runner` |
| 構造化出力（dict / Pydantic model 生成、選択肢の選択） | `kiarina-agi-runner` → `kiarina.agi.structured_output` |

### ワークフロー・プロンプト（詳細: [workflow-and-prompt.md](workflow-and-prompt.md)）

| やりたいこと | パッケージ / モジュール |
| --- | --- |
| 複数ステップの処理を workflow として組む | `kiarina-agi-flow` → `kiarina.agi.workflow` |
| プロンプト（LLM 1 呼び出しの単位）を定義する | `kiarina-agi-flow` → `kiarina.agi.prompt` |
| プロンプトを部品（section）に分割・重み付けする | `kiarina-agi-flow` → `kiarina.agi.section` / `section_container` |
| 状態遷移を管理する | `kiarina-agi-flow` → `kiarina.agi.state` / `state_machine` |

### ツール（詳細: [tools.md](tools.md)）

| やりたいこと | パッケージ / モジュール |
| --- | --- |
| ツールを定義・登録・実行する | `kiarina-agi-tool` → `kiarina.agi.tool` |
| ツール実行前後のフック | `kiarina-agi-tool` → `kiarina.agi.pre_hook` / `post_hook` |
| ツール実行のロギング | `kiarina-agi-tool` → `kiarina.agi.tool_logger` |
| LangChain ツールとの相互運用 | `kiarina-agi-tool` → `kiarina.agi.langchain_tool` |

### 基盤・データモデル（詳細: [foundation.md](foundation.md)）

| やりたいこと | パッケージ / モジュール |
| --- | --- |
| 実行コンテキスト（実行 ID、タイムゾーン等） | `kiarina-agi-base` → `kiarina.agi.run_context` |
| コスト記録・ロギング、リクエストログ、トークン計算 | `kiarina-agi-base` → `cost_recorder` / `cost_logger` / `request_logger` / `token_utils` |
| Message / Event / Content / History / FileInfo / ToolInfo のデータモデル | `kiarina-agi-data` |
| History / Event / Message / Content / FileInfo の関係と永続化 | [Data Model and History](data-model-and-history.md) |
| FileInfo の生成と実行時ポリシー | [FileInfo and Data Builder](file-info-and-data-builder.md) |
| 上記データの組み立て（builder / factory / loader） | `kiarina-agi-data-builder` |
| チャットモデル・テキスト埋め込みの抽象 | `kiarina-agi-text` → `kiarina.agi.chat_model` ほか |
| ファイル・キャッシュ・リポジトリ抽象 | `kiarina-agi-file` |

### モダリティ別 provider

音声・画像・動画は「model 抽象 + provider 実装」の対で構成されます。
新しい provider を追加・調査するときは該当パッケージの `*_model` / `*_provider` を見てください。

| モダリティ | パッケージ | 主な機能 |
| --- | --- | --- |
| 音声 | `kiarina-agi-audio` | ASR、TTS、VAD、話者交代検出、音声タグ付け、音声埋め込み |
| 画像 | `kiarina-agi-image` | 画像生成、検出、セグメンテーション、OCR、画像埋め込み |
| 動画 | `kiarina-agi-video` | 動画生成、動画ソース |

### インフラ・ユーティリティ

| やりたいこと | パッケージ |
| --- | --- |
| 外部サービスのクライアント設定・接続 | `kiarina-lib-*`（サービス名で選ぶ） |
| component registry / SettingsManager（名前→実装解決の仕組み） | `kiarina-utils-common` |
| ファイル I/O（エンコーディング・MIME 自動判定） | `kiarina-utils-file` |
| アプリ基盤（起動設定、ユーザーディレクトリ、単一インスタンス制御） | `kiarina-utils-app` |
| 国際化（i18n カタログ） | `kiarina-i18n` |
| 通貨・為替（コスト表示） | `kiarina-currency` |

## 共通パターン: registry + settings + impl

`kiarina.agi.*` の component family（agent / workflow / prompt / tool / hook / logger / provider 系）は
ほぼ同じ構造を持ちます。

- `Base<Name>` クラスと `@<name>` デコレータで実装を定義
- `<name>_registry` に名前で登録し、specifier（名前または import path）で解決
- `<Name>Settings` + `settings_manager` で default / presets / customs を構成
- 標準実装はソース内の隣接ディレクトリ `<name>_impl/` にある（例: `tool_impl/`, `prompt_impl/`）

`ComponentRegistry` の `expected_type` には具象クラスだけでなく、実行時の `isinstance` 検証に
使える `@runtime_checkable` な Protocol も渡せます。

この仕組みが kiari 側でどう使われるかは
[runtime-configuration-and-extensibility.md](../runtime-configuration-and-extensibility.md) を参照。

## Documented Versions

この文書群の記述が前提とするバージョン（= 執筆時点の kiari `uv.lock`）。
`uv.lock` の実バージョンと比較し、ずれていたら
[kiarina-python docs sync playbook](../../playbooks/kiarina-python-docs-sync.md) を実行してください。

| パッケージ | 文書化時バージョン |
| --- | --- |
| kiarina (メタ) | 2.19.0 |
| kiarina-agi-audio | 2.15.0 |
| kiarina-agi-base | 2.7.0 |
| kiarina-agi-data | 2.19.0 |
| kiarina-agi-data-builder | 2.19.0 |
| kiarina-agi-file | 2.16.0 |
| kiarina-agi-flow | 2.11.0 |
| kiarina-agi-image | 2.17.0 |
| kiarina-agi-runner | 2.14.0 |
| kiarina-agi-text | 2.19.0 |
| kiarina-agi-tool | 2.17.0 |
| kiarina-agi-video | 2.15.0 |
| kiarina-currency | 2.3.1 |
| kiarina-i18n | 2.3.1 |
| kiarina-lib-anthropic | 2.3.1 |
| kiarina-lib-cloudflare | 2.3.1 |
| kiarina-lib-cloudflare-d1 | 2.3.1 |
| kiarina-lib-falkordb | 2.3.1 |
| kiarina-lib-firebase | 2.3.1 |
| kiarina-lib-firebase-rtdb | 2.3.1 |
| kiarina-lib-google | 2.8.0 |
| kiarina-lib-openai | 2.3.1 |
| kiarina-lib-redis | 2.3.1 |
| kiarina-lib-redisearch | 2.17.0 |
| kiarina-lib-slack | 2.3.1 |
| kiarina-utils-app | 2.4.0 |
| kiarina-utils-common | 2.18.0 |
| kiarina-utils-file | 2.17.0 |
