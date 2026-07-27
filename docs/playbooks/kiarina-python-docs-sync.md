# kiarina-python Docs Sync Playbook

`docs/concepts/kiarina-python/` の文書群を、kiari が実際に依存している kiarina-python の
バージョンに追従させる手順です。

**トリガー**: `make upgrade`（= `mise run upgrade` / `uv lock --upgrade`）で
`kiarina-*` パッケージのバージョンが上がったとき。upgrade 後に次で検出できます。

```sh
git diff uv.lock | grep -B2 '^[-+]version' | grep -A2 'kiarina'
```

kiarina-python は仕様が頻繁に変わるため、upgrade を含むコミットではこの playbook の
実施（または未実施である旨の `NEXT_TASK.md` への記載）までをセットにします。

## 1. ずれの検出

kiari の `uv.lock` にロックされている実バージョンを取得します。

```sh
awk '/^\[\[package\]\]/{p=1} p&&/^name = /{n=$3} p&&/^version = /{if(n ~ /kiarina/) print n, $3; p=0}' uv.lock
```

これを [overview.md の Documented Versions](../concepts/kiarina-python/overview.md#documented-versions)
の表と比較します。すべて一致していれば、この playbook は完了です。

## 2. 差分の確認

ずれたパッケージごとに、変更内容を確認します（ローカルの
`~/src/github.com/kiarina/kiarina-python` を参照。checkout が古い可能性もあるので
必要なら先に `git pull`）。

1. **CHANGELOG**: ルートの `CHANGELOG.md`（プロジェクト全体、リリース単位）と、
   各パッケージの `packages/<package>/CHANGELOG.md`（パッケージ固有）を、
   文書化時バージョンから実バージョンまでの範囲で読む
2. **公開 API の差分**: 影響がありそうなら該当モジュールの `__init__.py`（`__all__`）を確認
3. 破壊的変更・リネーム・新機能のうち、kiari の文書記述に影響するものを洗い出す

## 3. 文書の更新

- 影響のあった記述を `docs/concepts/kiarina-python/` の各文書で修正する
  （overview.md の逆引き表 / agent-and-runner.md / workflow-and-prompt.md / tools.md / foundation.md）
- 新しいパッケージ・モジュールが増えていたら overview.md の逆引きに追加する
- 最後に overview.md の Documented Versions 表を、確認済みの実バージョンに更新する
  （**文書を直していないのに表だけ更新しない**こと。表は「ここまで文書が追従済み」の印）

## 4. 記録

- 差分確認で得た知見のうち仕組みとして残す価値のあるものは該当 `docs/` へ
- 未対応の破壊的変更や、kiari 側コードへの影響が残る場合は `NEXT_TASK.md` に記載
