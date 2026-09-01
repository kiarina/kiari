# 次回リリース前に timezone rename の公開依存を確定する

## 背景

2026-08-30 に `RunContext` / `RunContextSettings` / `RunOptions` の `time_zone` を
`timezone` へ破壊的に変更した。kiari の開発環境は kiarina を git HEAD から解決するため
（`pyproject.toml` の `[tool.uv.sources]`）、この変更は未リリースの kiarina API へ
依存したままでも動いてしまう。

`pyproject.toml` の `kiarina[all]>=X` は PyPI 利用者に対する契約で、tag を打つと
`release-pypi.yml` が `--no-sources` で解決し直すため、floor が古いままだと publish 前に落ちる。
詳細は `docs/runbooks/release.md` を参照する。

## やること

- [ ] `timezone` を含む kiarina-python をリリースする
- [ ] `pyproject.toml` の `kiarina[all]` の下限を、そのリリース version へ上げる
- [ ] release workflow の `--no-sources` 検証を通す
- [ ] リリース後、`CHANGELOG.md` に破壊的変更として記載されていることを確認する

## 進捗

未着手。kiari 側の rename は完了済み。

## 申し送り

- このタスクは次回リリースの前提条件であり、単独では完了しない。リリース作業を始めるときに
  最初に消化する
