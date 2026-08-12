# HISTORY

## 2026-08-10: Dependabot 更新とセキュリティ修正

- Dependabot PR 10 件を取り込み、GitPython 3.1.58、pypdf 6.15.0、cryptography 50.0.0、
  LangChain 1.3.9、GitHub Actions などへ更新した
- 拡張した依存範囲を lockfile に反映し、mypy 2.3.0、puremagic 2.2.0、Rich 15.0.0 で
  lint・通常テスト 539 件・package build が成功することを確認した
- Pillow 12.3.0 は kiarina-agi-data-builder 2.19.0 の `pillow<12` 制約と競合するため、
  上流制約の更新後に対応する残タスクとした

## 2026-08-10: schedule modeの公開APIと外部stop_event注入

- `run_schedule`を`_operations/`から`_helpers/`へ移し、`kiari.cli.schedule`の公開APIとして
  exportした。外部runtime（Spirits GardenのBody常駐化）が私有パスへ直接依存していた状態を解消する
- `run_schedule`と`graceful_shutdown`へ外部`stop_event`注入を追加した。SIGINTと同じイベントを
  共有するため、外部停止でも実行中のrequestは完了してからloopを抜ける
- テストは公開面からのimportへ切り替え、外部stop_eventでの停止テストを追加した

## 2026-07-29: Pub/Subの処理成功後ACKを追加

- watch処理の成功後に`WatchEvent.acknowledge()`、失敗・キャンセル・queue timeout時に
  `WatchEvent.release()`を呼ぶライフサイクルを追加した
- Pub/Sub watcherは受信直後のACKを廃止し、処理中のack deadlineを延長したうえで、成功時ACKまたは
  失敗時の即時再配信を行うようにした

## 2026-07-27 依存パッケージを更新

- `make upgrade` で依存を更新し、kiarina 2.19.0、Ruff 0.16.0、FastAPI 0.140.0、
  Streamlit 1.60.0 などへ追従した
- kiarina 2.19.0 の capability-aware PDF / video analysis bundle、FileBundle manifest、
  OpenAI cost record の変更を確認し、kiarina-python concept 文書を同期した
- lint・mypy、通常テスト 540 件、package build が成功した

## 2026-07-26 テストアセットを外部配布へ移行

- テストで使う text / image / audio / PDF / video の5アセットを `kiarina/test-assets` の
  `kiari-assets-v1` から取得する構成へ移行した
- `make download-test-assets` と `mise run setup` でリポジトリ名に対応するアセットを
  `tests/assets/` へ展開し、取得失敗を明示的なセットアップ失敗として扱うようにした
- GitHub Actions の通常CIとPyPIリリース検証でも、テスト実行前にアセットを取得するようにした
- リポジトリ管理下に残っていたテスト用メディアを削除した

## 2026-07-26 静的解析設定を kiarina-python と同期

- Ruff の検査対象を pycodestyle、Pyflakes、isort、flake8-bugbear、flake8-comprehensions、pyupgrade、Ruff 固有ルールへ拡張した
- mypy を strict mode にし、`kiari/` 本体の既存コードを strict 検査へ適合させた
- lint 実行時の暗黙 auto-fix を廃止し、書き換えを `mise run format` に限定した
- 型エイリアスを Python 3.12 の `type` 文へ統一し、非同期 task と外部ライブラリ境界の型を明示した
- `kiarina[all]` を 2.18.0 へ更新し、runtime-checkable Protocol を受け取れる
  `ComponentRegistry` に合わせて registry の `type-abstract` 抑制を削除した

## 2026-07-25 Chrome Bridge SDK 0.4 対応

- `chrome-bridge-sdk` / server の依存を 0.4 系へ更新し、browser-native dialog を支配的な PageState として表示するようにした
- `dialog_respond` action を追加し、dialog snapshot の厳密な ref を使った accept / dismiss と prompt text の応答を利用可能にした
- dialog 応答後の document snapshot に付随する recording / download metadata を tool 出力へ保持した
- 実 SDK・実 extension integration test に confirm dialog の観測と応答を追加した

## 2026-07-24 Streamlit 実行モードのリファクタ移植

- `kiari/streamlit` を独立した Streamlit project、`kiari/cli/streamlit` を server 起動 interface として実装した
- CLI で検証済みの Profile 名と RunOptions を version 付き・permission `0600` の startup payload で child process へ渡す境界を追加した
- browser-session / OIDC の差し替え可能な認証、所有者付きでグローバルに一意な agent ID の作成・選択・削除を追加した
- GUI console、Event streaming、添付、ASR/TTS、履歴操作、session-local RunOptions 更新、agent 単位の排他実行を現行 kiarina agent API 上へ移植した

## 2026-07-24 FastAPI 実行モードのリファクタ移植

- `kiari/fastapi` を独立した ASGI project、`kiari/cli/fastapi` を server 起動 interface として実装した
- CLI で検証済みの Profile 名と RunOptions を version 付き・permission `0600` の一時 JSON payload に固定し、reload / 複数 worker へ同じ値を引き渡す境界を追加した
- health endpoint、NDJSON Event stream、request 単位の実行設定・serialized Event・run kwargs、差し替え可能な FastAPIHandler / Authenticator を現行 kiarina agent API 上へ移植した
- none / Bearer 認証、streaming error Event、History 保存、cost flush、worker lifespan の runtime 初期化と finalizer を追加した

## 2026-07-24 kiarina-agi-data のモデル関係を文書化

- `History → Event → Message → Content → FileInfo` の所有関係と、各型の責務を整理した
- Event stream、tool call loop、History 永続化、FileInfo pool の hydrate / dehydrate を開発ガイドへ集約した

## 2026-07-24 FileInfo と data-builder の開発ガイド整備

- `FileInfo`、ファイル I/O、builder の package 境界と、kiari の attachment から agent pre-run、provider 変換までの処理順を文書化した
- `pinned`、`inline`、`metadata_only`、`content_only`、`no_merge`、`group`、`unique_key`、`keep_from_end` の作用範囲と相互作用を整理した

## 2026-07-24 Chrome Bridge SDK ベースの chrome tool

- `chrome-bridge-sdk` 0.3 系を導入し、単一の `chrome` tool から browser instance、tab、accessibility snapshot、strict ref 操作、navigation、wait、upload/download、screenshot、console log、video recording の全23操作を利用可能にした
- 各 action が独立した exclusive session を取得・解放し、SDK エラーの `code`、`retryable`、`outcome_unknown` を tool error に保持するようにした
- screenshot は画像 attachment、snapshot は accessibility tree、その他の typed SDK result は用途別テキストまたは snake_case JSON として返すようにした
- 未使用だった Playwright/CDP ベースの Chrome 起動・process kill と Chrome finalizer を削除し、ユーザーの Chrome と SDK managed server を kiari が終了しない所有権へ変更した
- mock ベースの Chrome tool テストを、実 SDK・実 extension・専用 loopback fixture を通す `costly` integration test へ置き換え、`make chrome_test` で明示実行できるようにした
- Chrome tool と Chrome Bridge の責務境界、session/target/ref、error、ownership、実環境テスト、SDK 更新手順を concept 文書へ集約した

## 2026-07-19 依存整理と kiarina[all] への移行

- pyproject.toml の dependencies を 82 → 34 個に削減。全 import 実測(kiari/tests の直接 import + kiarina-python 側の未宣言遅延 import + 設定ファイルの文字列指定)に基づき、完全未使用のものを削除
- kiarina を 2.14.0 → 2.16.0 に upgrade し、`kiarina[all]` に切り替え。kiarina が遅延 import する SDK 群(openai / google-genai / onnxruntime / langchain-anthropic 等 / pypdf)の直接宣言は extras に委譲
- 例外として残したもの: `puremagic`(kiarina-utils-file 2.16 時点でも未宣言の遅延 import)、`audioop-lts`(kiari 直接利用の pydub が Python 3.13 で必要)
- fastapi / uvicorn / streamlit は未実装 CLI スタブ用に維持。streamlit-aggrid は削除
- docs sync playbook 実施済み(overview.md の Documented Versions を 2.16 系に更新。2.15/2.16 の変更は文書本文に影響なし)
- どこからも参照されていなかった tests/data/python/mcp_server_math.py を削除(依存 `mcp` は langchain-mcp-adapters 削除で消えた)
# 2026-08-12 HistoryRepositoryのGCS / Firebase Storage境界を分離

- GCS HistoryRepositoryをAssetRepository経由からGoogle Cloud Storage clientの直接利用へ変更し、
  agentのdata / cache asset権限からHistory制御状態を分離した
- Firebase ID tokenと更新可能なtoken providerに対応するFirebase Storage HistoryRepositoryを
  `impl/history_repository_impl/firebase_storage/`へ追加した
- GCS / Firebase StorageともRunContextからprovider固有のobject nameを解決し、History JSONを
  round-tripするcontract testを追加した
