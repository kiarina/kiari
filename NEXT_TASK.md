# NEXT TASK

## Pillow の Dependabot アラートが閉じるのを確認する

- v0.2.0（`15c4d3d`）で `uv.lock` の Pillow は `12.3.0` になり、open だった 18 件
  （high 13 / moderate 5、すべて Pillow、manifest は `uv.lock`）の脆弱範囲からは全件外れた。
  修正版はいずれも 12.3.0 以下
- ただし 2026-08-21 03:00 時点でアラートは 18 件 open のまま。GitHub の default branch の
  dependency graph が古い snapshot（`pillow 11.3.0`）を返しており、その再スキャン待ち
- GitHub 側は変更自体を認識している（compare API は uv.lock の 11.3.0 → 12.3.0 を返す）。
  再スキャンを強制する手段は見つかっていないため、時間をおいて再確認する

```sh
# open なアラート件数（0 になれば完了）
gh api repos/kiarina/kiari/dependabot/alerts --paginate \
  -q '[.[] | select(.state=="open")] | length'

# default branch の graph が見ている Pillow（12.3.0 になれば反映済み）
gh api repos/kiarina/kiari/dependency-graph/sbom \
  -q '.sbom.packages[] | select(.name|test("pillow";"i")) | .versionInfo'

# GitHub が変更を認識しているかの確認
gh api "repos/kiarina/kiari/dependency-graph/compare/58b86f3...15c4d3d" \
  -q '.[] | select(.name|test("pillow";"i")) | "\(.change_type) \(.name) \(.version) \(.manifest)"'
```

- 長期間閉じない場合は、`uv.lock` を触る次のコミット（依存更新など）を push して
  graph の再取り込みを促すか、GitHub Support へ問い合わせる
