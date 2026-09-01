# kiapi の Web 検索が空結果になる原因を確認する

## 背景

2026-08-30 に MacBook Pro M1 Max で通常テストを実行したところ、
`tests/impl/web_impl/kiapi/_models/test_kiapi_web.py::test_search` が
`Python programming language` に対して空配列を返し、単独再実行でも再現した。
kiapi の fetch と、このテスト以外の通常テストは成功している。

kiari 側の実装が原因か、kiapi server / 検索 provider の状態が原因かを切り分けていない。

## やること

- [ ] kiapi server の稼働状態と、検索 provider の設定・API キー・残量を確認する
- [ ] kiapi へ直接同じクエリを投げ、kiari を介さずに空結果が再現するか確かめる
- [ ] 原因が kiapi 側なら kiapi のタスクへ引き継ぎ、kiari 側なら該当実装を修正する
- [ ] 外部サービスの状態に左右されるテストを、通常テストに残すか marker で分離するか決める

## 進捗

未着手。2026-08-30 時点の再現確認のみ。

## 申し送り

- 空結果は例外にならないため、テストが落ちるまで劣化に気づけない。原因確定後、
  検索経路の失敗をどう表面化させるかも合わせて決める
