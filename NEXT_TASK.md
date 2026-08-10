# NEXT TASK

## Pillow の Dependabot アラート解消

- GitHub の Pillow アラート 36 件は `12.3.0` で修正されるが、kiari が利用する
  `kiarina-agi-data-builder==2.19.0` の `pillow>=11.3.0,<12` 制約により upgrade できない
- `kiarina-python` 側で Pillow 12 系との互換性を検証し、`kiarina-agi-data-builder` と関連 package の
  制約を更新してリリースする
- kiari で新しい kiarina release を取り込み、`uv lock --upgrade-package pillow` と `make ci` を実行し、
  lockfile が Pillow 12.3.0 以上になったことと Dependabot アラートの解消を確認する
