# AGENTS.md

このリポジトリで作業するエージェント向けのガイドラインです。

## 作業前に読むもの

あらゆるタスクを開始する前に、下記を必ず把握してください。

- `README.md`
- `pyproject.toml`
- `mise.toml`
- `.mise/tasks/`
- `Makefile`
- `ARCHITECTURE.md`
- `NEXT_TASK.md`

完了タスク・実測値・過去の意思決定を辿るときは `HISTORY.md`（作業手順は `docs/` を正典とする）。

## 設計・実装するとき

kiari は kiarina-python（`~/src/github.com/kiarina/kiarina-python`）の上に構築されています。
機能の設計・実装・調査に入る前に、前提知識として
`docs/concepts/kiarina-python/overview.md`（パッケージ全体像と逆引き）を必ず読んでください。
個別領域の詳細は「docs 以下の参照ガイド」から該当文書を辿ります。

## 依存するとき

**kiarina は PyPI ではなく git HEAD から解決します**（`pyproject.toml` の
`[tool.uv.sources]`）。kiarina-python 側の変更を、リリース前にここで評価するためです。
kiarina に入れた機能をすぐ kiari で使って確かめられる代わりに、**未リリースの API へ
依存したまま気づかない**状態になり得ます。

`pyproject.toml` の `kiarina[all]>=X` は PyPI の利用者に対する契約で、開発環境では
一度も検証されません。守るのはリリース手順の責任です
（`docs/runbooks/release/README.md`）。tag を打つと `release-pypi.yml` が
`--no-sources` で解決し直して CI を回すので、floor が嘘なら publish 前に落ちます。

`uv.lock` には commit が固定されるため、HEAD へ追随するのは `make upgrade` を
叩いたときだけです。

## テストするとき

Settings クラスの既定値、環境変数の読み込み、フィールド検証を直接確認するテストは追加しません。
Settings を利用する component や機能の公開境界で、必要な設定値が挙動へ反映されることを確認します。

Chrome Bridge tool の SDK・extension 互換性は mock で代替せず、`costly` marker 付きの実環境
integration test で確認します。通常のテストからは skip し、環境を準備して `make chrome_test` で
明示的に実行します。

## コミットするとき

**次の作業は別の担当者に引き継がれる**前提で作業してください。コミットの際、次に着手する人へ
追加で伝えるべきことがあれば `NEXT_TASK.md` に記載してください（残タスク・未検証の懸念・
踏んだ落とし穴・次の一手など）。仕組みとして残す価値のある知見は該当する `docs/` へ、
完了した作業の記録は `HISTORY.md` へ振り分け、`NEXT_TASK.md` は残タスクに保ちます。

## docs 以下の参照ガイド

作業内容に応じて、`docs/` 以下の該当ドキュメントを着手前に読んでください。
`docs/` 以下にドキュメントを更新した場合は、ここに、読む条件とファイルパスを記載してください。

- agent / task runner / structured output に関わる作業をするとき
  `docs/concepts/kiarina-python/agent-and-runner.md`
- workflow / prompt / section / state に関わる作業をするとき
  `docs/concepts/kiarina-python/workflow-and-prompt.md`
- ツール・フックの追加・変更をするとき
  `docs/concepts/kiarina-python/tools.md`
- `kiari/impl/tool_impl/` のツールを追加・変更するとき
  `docs/concepts/tool-implementation-patterns.md`
- Chrome tool、`kiari.lib.chrome`、Chrome Bridge SDK・extension 連携を追加・変更するとき
  `docs/concepts/chrome-tool-and-bridge.md`
- RunContext・コスト/ログ・Message/Event/History 等のデータモデルに関わる作業をするとき
  `docs/concepts/kiarina-python/foundation.md`
- History・Event・Message・Content・FileInfo の関係や永続化境界に関わる作業をするとき
  `docs/concepts/kiarina-python/data-model-and-history.md`
- FileInfo・attachment・file builder・file segment・ファイル上限調整に関わる作業をするとき
  `docs/concepts/kiarina-python/file-info-and-data-builder.md`
- `make upgrade` で `kiarina-*` のバージョンが上がったとき、または kiarina-python 文書群と `uv.lock` のバージョンがずれているとき
  `docs/playbooks/kiarina-python-docs-sync.md`
- `.mise/tasks/`・`Makefile`・CI ワークフローを追加・変更するとき
  `docs/concepts/task-runner-conventions.md`
- batch / console / watch / schedule の実行モードや agent engine の駆動に関わる作業をするとき
  `docs/concepts/execution-modes.md`
- 実行設定・component 設定・実装の差し替え(拡張ポイント)に関わる作業をするとき
  `docs/concepts/runtime-configuration-and-extensibility.md`
- リリース作業をするとき
  `docs/runbooks/release/README.md`
