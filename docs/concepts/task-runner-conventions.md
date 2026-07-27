# Task Runner Conventions

この文書は、kiari における mise tasks と Makefile の使い分けの規約を説明します。

## 原則

- **ロジックはすべて mise tasks に書く。** `.mise/tasks/` 以下のスクリプトが処理の唯一の定義場所です。引数やフラグを持って構いません。
- **Makefile は薄い入口。** 開発タスクは `mise run <task>` へ委譲し、依存関係の確認・同期だけは `uv` を直接呼び出します。シェルロジックは書きません。
- CI (GitHub Actions) からも mise tasks を直接呼び出します。

## mise tasks

タスクは `.mise/tasks/` 以下に bash スクリプトとして配置します。

- 冒頭に `#MISE description=...` と、引数・フラグがあれば `#USAGE` 宣言を書きます。
- `set -euo pipefail` を必ず指定します。
- コマンドは文字列連結 + `eval` ではなく、bash 配列で組み立てます。
- 関連するタスクはディレクトリで namespace 化します(例: `changelog/extract` → `mise run changelog:extract`)。

主なタスク:

| タスク | 内容 |
|---|---|
| `setup` | 開発環境の構築(mise tools、依存関係、テストアセット) |
| `format` | ruff check --fix + ruff format(コードを書き換える) |
| `lint` | ruff check + ruff format --check + mypy(書き換えない) |
| `test` | pytest 実行。`--coverage` / `--costly` / `--verbose` / `--path` フラグあり |
| `ci` | lint → test --coverage → build |
| `build` / `publish` | パッケージのビルドと PyPI 公開 |
| `changelog:*` / `pyproject:*` | リリース用のバージョン操作 |
| `test-assets:*` / `test-settings:*` | テストアセットと暗号化テスト設定の管理 |

静的検査は次の境界で実行します。

- Ruff は `kiari/` と `tests/` を検査し、pycodestyle、Pyflakes、isort、flake8-bugbear、
  flake8-comprehensions、pyupgrade、Ruff 固有ルールを有効にする
- mypy は `kiari/` 本体を strict mode で検査する
- `lint` はファイルを書き換えず、auto-fix は `format` だけが実行する

## Makefile

Makefile は mise を知らない人でも `make` だけで日常の開発操作を行えるようにするための入り口です。ターゲット構成は kiarina-python と揃えます。

- 開発タスクは対応する `mise run <task>` を呼び出します。
- `list` / `update` / `upgrade` は、依存関係の状態を確認・同期するため `uv` を直接呼び出します。
- `check` は format と lint を順に実行し、既定ターゲットとして使います。
- ターゲットは引数を受け取りません。汎用フラグ付きで呼びたい場合は mise task を直接使います(例: `mise run test --costly`)。
- 環境準備が必要な定型テストには、対象 path とフラグを固定した薄い専用ターゲットを設けられます。`chrome_test` は実 Chrome Bridge 用の例です。
- レシピに条件分岐などのシェルロジックを書いてはいけません。

## 使い分けの目安

```sh
make            # format → lint
make ci         # CI と同じチェック (lint → test --coverage → build)
mise run ci     # CI と同じチェック (lint → test --coverage → build)
mise run test --costly   # フラグが必要な呼び出しは mise を直接使う
make chrome_test         # 実 Chrome Bridge 環境で costly integration test を実行
```
