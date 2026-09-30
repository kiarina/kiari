# node_id を runner_id に置き換える kiarina の変更に合わせる

## 完了条件

kiarina の `RunContext.node_id` 廃止・`runner_id` 追加（kiarina 2.34.0 で公開済み。2026-09-30）に
kiari と kiari-plugins を合わせ、テストが通り、リリースしていること。

## 背景

2026-09-30 にオーナーと整理した。RunContext の `node_id` は表示にしか使われておらず、`runner_id`（実行している主体）に戻す。
ファイルの判定（`BaseAgent._update_file_infos`）は kiarina 側で node の比較をやめ、履歴のファイルを全部手元のものとして扱う。
そのため kiari が runner_id をマシンごとに固定する必要はなく、`node_id.txt` の保存は要らなくなる。

## やること

- `RunOptions.node_id` → `runner_id`（`core/profile/_schemas/run_options.py`）
- `setup_runtime`: `node_id.txt` の読み書きと設定への `node_id` の書き込みを消す。`runner_id` が指定されたときは、
  RunContext を作る所へ渡す（指定がなければ kiarina の既定の ULID）
- CLI の `--runner-id`（`cli/_decorators/common_options.py`）は `RunOptions.runner_id` に入れる。i18n の `node_id_help` を直す
- 表示: `impl/tool_logger_impl/default`、`impl/chat_logger_impl/default`、`cli/console/console_renderer/_helpers/render_console_status.py`
- テスト: `tests/conftest.py`、`tests/core/runtime/_helpers/test_setup_runtime.py`
- kiari-plugins: `extension_command/text_embedding.py` の `_create_run_context` の `node_id`（`or agent_id` の代入は外す）

## 申し送り

- kiarina 2.34.0 は公開済み（kiarina-agi-base・kiarina-agi-data・kiarina-agi-runner と meta package）。依存の下限を 2.34.0 に上げてから直す
- kiarina 2.34.0 では `get_node_id()` と設定の `node_id` が無くなり、`FileInfo.node_id` は `str | None = None`、`BaseAgent._update_file_infos` は node に関係なく全ファイルを処理する
