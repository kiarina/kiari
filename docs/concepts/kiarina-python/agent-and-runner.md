# Agent and Runner (kiarina-agi-runner)

エージェントの実行エンジン。kiari の各実行モード（batch / console / watch / schedule）は
最終的にここへ到達します。実行モード側の話は [execution-modes.md](../execution-modes.md) を参照。

前提バージョンは [overview.md](overview.md#documented-versions) を参照。

## kiarina.agi.agent

エージェント実行の中核。

- 実行ヘルパー: `run_agent()`（Event の AsyncIterator を返す）、`invoke_agent()`、`stream_agent()`
- `run_agent(history, *, run_context, chat_options, prompt_options, workflow_options, tool_options, agent_options, cost_recorder, stop_event, ...)` —
  `History` を入力に、agent ループを回して `Event` を流す
- 実装定義: `BaseAgent` を継承し `agent_registry` に登録。`AgentSettings` + `settings_manager` で
  default / presets / customs を構成（[共通パターン](overview.md#共通パターン-registry--settings--impl)）
- `AgentContext`: 実装に渡される実行時コンテキスト
- `MissingToolsError`: 要求されたツールが解決できないときの例外

標準実装: `packages/kiarina-agi-runner/src/kiarina/agi/agent_impl/vanilla/`

kiari 側の呼び出し例:

- `kiari/cli/batch/_operations/run_batch.py`
- `kiari/cli/console/_operations/run_console.py`
- `kiari/cli/watch/_operations/run_watch.py`
- `kiari/cli/schedule/_operations/run_schedule.py`

## kiarina.agi.task_runner

エージェント実行をタスクとして走らせるヘルパー: `run_task()` / `invoke_task()` / `stream_task()`。
テスト: `packages/kiarina-agi-runner/tests/task_runner/`

## kiarina.agi.structured_output

LLM から構造化された結果を得るヘルパー。

- `generate_dict()`: dict を生成
- `generate_model()`: Pydantic model を生成
- `select_option()`: 選択肢から選ばせる

テスト: `packages/kiarina-agi-runner/tests/structured_output/`
