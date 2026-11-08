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

## 2026-11-09 の追記（依存の定期保守）

kiarina を `4aed3a00`（2.36.1）から `17d89da8`（2.41.0）へ上げた。文書は直しておらず、ずれは runner・base の 2 つから
次の 11 に広がった（`mise run ci` は 561 passed / 9 skipped で、kiari のコードは壊れていない）。

| パッケージ | 文書の版 | lock の版 |
| --- | --- | --- |
| kiarina (meta) | 2.36.1 | 2.41.0 |
| kiarina-agi-base | 2.28.0 | 2.34.0 |
| kiarina-agi-data | 2.36.0 | 2.38.0 |
| kiarina-agi-data-builder | 2.32.0 | 2.37.0 |
| kiarina-agi-file | 2.32.0 | 2.41.0 |
| kiarina-agi-flow | 2.11.0 | 2.37.0 |
| kiarina-agi-image | 2.28.0 | 2.40.0 |
| kiarina-agi-runner | 2.21.0 | 2.38.0 |
| kiarina-agi-text | 2.36.1 | 2.41.0 |
| kiarina-agi-tool | 2.22.0 | 2.40.0 |
| kiarina-lib-google | 2.8.0 | 2.40.0 |

2.37.0〜2.41.0 の破壊的変更（`FileInfo.asset_hash`、`opencv-python`・`google-api-python-client`・`langchain` を既定の依存から外した）は
kiarina-python の root の `CHANGELOG.md` にある。`langchain_tool` の削除は `f462ca4` で文書から消し済み。
