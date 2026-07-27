# Workflow and Prompt (kiarina-agi-flow)

エージェントの 1 イテレーションを構成する workflow / prompt / section / state の各層。
agent（[agent-and-runner.md](agent-and-runner.md)）がループを回し、workflow がループ内の
処理手順を、prompt が LLM 呼び出しを、section がプロンプト本文の部品を担います。

前提バージョンは [overview.md](overview.md#documented-versions) を参照。

## kiarina.agi.workflow

処理フローの単位。

- 定義: `@workflow` デコレータ、または `BaseWorkflow` 継承 + `workflow_registry` 登録
- 実行: `run_workflow()` / `invoke_workflow()` / `stream_workflow()`
- 構成: `WorkflowSettings` + `settings_manager`、specifier で解決
  （[共通パターン](overview.md#共通パターン-registry--settings--impl)）

標準実装: `packages/kiarina-agi-flow/src/kiarina/agi/workflow_impl/vanilla/`
テスト: `packages/kiarina-agi-flow/tests/workflow/`

## kiarina.agi.prompt

LLM 1 呼び出しの単位。API 形状は workflow と同型
（`@prompt` / `BasePrompt` / `run_prompt()` / `invoke_prompt()` / `stream_prompt()` /
`prompt_registry` / `PromptSettings`）。

標準実装: `packages/kiarina-agi-flow/src/kiarina/agi/prompt_impl/`（`vanilla/`, `structured/`）
テスト: `packages/kiarina-agi-flow/tests/prompt/`, `tests/prompt_impl/`

kiari 側の利用箇所は `grep -r 'kiarina.agi.prompt' kiari/` で確認。

## kiarina.agi.section / section_container

プロンプト本文を部品化する仕組み。

- `BaseSection` + `SectionContext`、`Weight` による優先度・重み付け
- `SectionContainer` が section 群を束ねて本文を組み立てる

実装例・テスト: `packages/kiarina-agi-flow/src/kiarina/agi/section_impl/`,
`packages/kiarina-agi-flow/tests/section/`, `tests/section_container/`

## kiarina.agi.state / state_machine

状態遷移の管理。

- `@state` デコレータ / `BaseState` + `StateContext` で状態を定義
- `StateMachine` が遷移を駆動

実装例・テスト: `packages/kiarina-agi-flow/src/kiarina/agi/state_impl/`,
`packages/kiarina-agi-flow/tests/state/`, `tests/state_machine/`
