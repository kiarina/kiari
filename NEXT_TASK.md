# NEXT TASK

## kiapi の Web 検索が空結果になる原因を確認する

2026-08-30 に MacBook Pro M1 Max で通常テストを実行したところ、
`tests/impl/web_impl/kiapi/_models/test_kiapi_web.py::test_search` が
`Python programming language` に対して空配列を返し、単独再実行でも再現した。kiapi の fetch と、
このテスト以外の通常テストは成功している。kiapi server / 検索 provider の現在の状態を確認する。
