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

- [x] `timezone` を含む kiarina-python をリリースする（2.28.0 で公開済み）
- [x] `pyproject.toml` の `kiarina[all]` の下限を、そのリリース version へ上げる
  （2026-09-15 に RTDB watcher の追従で `>=2.29.0` へ上げた。2.29.0 は 2.28.0 を含む）
- [ ] release workflow の `--no-sources` 検証を通す
- [ ] リリース後、`CHANGELOG.md` に破壊的変更として記載されていることを確認する

## 進捗

kiari 側の rename は完了済み。下限は 2.29.0 まで上げた。残りはリリース時の `--no-sources` 検証と CHANGELOG の確認。

## 申し送り

- このタスクは次回リリースの前提条件であり、単独では完了しない。リリース作業を始めるときに
  最初に消化する
