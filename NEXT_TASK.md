# NEXT TASK

## Pillow の Dependabot アラート解消の確認

- `kiarina[all]>=2.25.0` への upgrade で `kiarina-agi-data-builder==2.21.1` を取り込み、
  `uv.lock` の Pillow は `12.3.0` になった（`make ci` 通過済み）
- 残りは push 後に GitHub の Dependabot アラート 36 件が解消されたことを確認するだけ
