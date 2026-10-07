# kiarina-agi-runner と kiarina-agi-base の文書を lock の版に同期する

## 背景

`docs/concepts/kiarina-python/overview.md` の Documented Versions が、`uv.lock` より古いまま残っている
（2026-10-08、kiarina 2.36.0 への更新時に確認）。

| パッケージ | 文書の版 | lock の版 |
| --- | --- | --- |
| kiarina-agi-runner | 2.21.0 | 2.34.0 |
| kiarina-agi-base | 2.28.0 | 2.34.0 |

2.36.0 への更新では、変わった kiarina（meta）・kiarina-agi-data・kiarina-agi-text だけを同期した。
この 2 つは今回の更新の前からずれていた。

## やること

`docs/playbooks/kiarina-python-docs-sync.md` に沿って、kiarina-python の CHANGELOG（root と各パッケージ）を
文書の版から lock の版まで読み、`docs/concepts/kiarina-python/` の該当する文書を直してから、表の版を上げる。
