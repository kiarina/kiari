# Tools (kiarina-agi-tool)

エージェントに与えるツールの定義・実行・フック・ロギング。
kiari は独自ツールを多数実装しており、新しいツールを作るときの実例はまず kiari 側を見るのが早いです。

前提バージョンは [overview.md](overview.md#documented-versions) を参照。

## kiarina.agi.tool

- 定義: `@tool` デコレータ、または `BaseTool` 継承 + `tool_registry` 登録
- 実行: `run_tool()`。入出力は `ToolInput` / `ToolOutput`（`ToolOutputLike` から正規化）
- `ToolContext`: 実装に渡される実行時コンテキスト
- `AdditionalFieldConfig`: スキーマへの追加フィールド設定
- 例外: `ToolError`（ツール内エラー）、`ToolNotFoundError`
- 構成: `ToolSettings` + `settings_manager`、`ToolSpecifier` で解決。
  pre/post hook は `PreHookBinding` / `PostHookBinding` でツールに束ねる
  （[共通パターン](overview.md#共通パターン-registry--settings--impl)）

標準実装（kiarina-python 側）: `packages/kiarina-agi-tool/src/kiarina/agi/tool_impl/`

kiari 側の実装例（`kiari/impl/tool_impl/`）:

- `web/` — 検索・フェッチを持つ複合アクション型ツール（`_types/action.py`, `_operations/`, `_schemas/`, `_models/` の分割例）
- `subprocess/` — 実行・出力取得・キャンセルなどを持つ複合アクション型ツール
- `text_file_view/`, `text_file_edit/`, `pdf_file_view/`, `image_file_view/`, `audio_file_view/`, `video_file_view/` — ファイル閲覧・編集系
- `image_generate/`, `video_predict/` — 生成・推論系
- `gui/`, `change_directory/` — 環境操作系

kiari 側で採用している単機能型と複数アクション型の構成、選択基準、追加手順は
[Tool Implementation Patterns](../tool-implementation-patterns.md) を参照。

## kiarina.agi.pre_hook / post_hook

ツール実行前後に挟む処理（確認・変換・記録など）。

- 定義: `@prehook` / `@posthook`、または `BasePreHook` / `BasePostHook`
- 実行: `run_pre_hooks()` / `run_post_hooks()`。`PreHookContext` / `PostHookContext` を受け、
  `PreHookOutput` / `PostHookOutput` を返す
- 例外: `PreHookError` / `PostHookError`

実装例: `packages/kiarina-agi-tool/src/kiarina/agi/pre_hook_impl/`, `post_hook_impl/`

## kiarina.agi.tool_logger

ツール実行のロギング抽象。kiari 側の実装: `kiari/impl/tool_logger_impl/`

## kiarina.agi.langchain_tool

`LangChainTool`: LangChain のツールを kiarina のツールとして扱うアダプタ。
テスト: `packages/kiarina-agi-tool/tests/langchain_tool/`
