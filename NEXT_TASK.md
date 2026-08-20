# NEXT TASK

## Pillow の Dependabot アラート 18 件が open のまま残っている

**実体としては修正済み。GitHub 側の dependency graph が 2026-08-10 時点の
snapshot から更新されないため、アラートの状態だけが古い。**

### 確認済みの事実

- `uv.lock` の Pillow は `12.3.0`（v0.2.0 / `15c4d3d` 以降）。18 件の脆弱範囲はすべて
  `< 12.3.0` 以下なので全件が対象外
- Dependabot の uv updater 自身がそう報告している
  （job 1534654736 / run 32430028113 のログ）:

  ```
  INFO Checking if pillow 12.3.0 needs updating
  INFO Latest version is 12.3.0
  INFO no security update needed as pillow is no longer vulnerable
  ```

  この job が `failure` 扱いなのは「更新不要」を error として記録する Dependabot の仕様で、
  解決の失敗ではない
- 一方 `dependency-graph/sbom` は今も 8/10 の lock の内容を返す
  （pillow 11.3.0 / kiarina 2.19.0 / pypdf 6.15.0 / streamlit 1.60.0）。
  アラートはこの snapshot を基準に判定されるため閉じない
- 8/10 に 18 件が `fixed` で自動クローズされた実績があるので、仕組み自体は動く
- `uv.lock` のサイズ（624KB）・フォーマット（`version = 1` / `revision = 3`）は
  8/10 から実質変わっておらず、パース不能になった形跡はない

### 試して効果がなかったこと

- Insights → Dependency graph → Dependabot の "Check for updates"
  （`pip`/`uv` の job は success するが graph は動かない）
- アラート画面からの security update 実行（上記の「no update needed」で終わる）
- 設定を `package-ecosystem: "pip"` → `"uv"` へ変更して push（`1a141a9`）。
  これ自体は正しい修正（pip updater は pyproject しか読まず uv.lock を更新できない）で、
  以後 uv.lock 由来の更新 PR が出るようになるが、graph の再取り込みは起きなかった

### 次の一手（どれか）

1. 放置して再確認する。実害はなく、次に `uv.lock` を変更する commit を push した際に
   再取り込みされる可能性が高い
2. 18 件を "This alert is inaccurate or incorrect" で dismiss し、コメントに
   上記 job ログを残す（バッジを消したい場合）
3. GitHub Support へ問い合わせる（graph が 10 日以上更新されない件として）

```sh
gh api repos/kiarina/kiari/dependabot/alerts --paginate \
  -q '[.[] | select(.state=="open")] | length'
gh api repos/kiarina/kiari/dependency-graph/sbom \
  -q '.sbom.packages[] | select(.name|test("^pillow$";"i")) | .versionInfo'
```
