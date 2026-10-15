# chrome-bridge-sdk 0.6 に上げる

## 背景

chrome-bridge 0.6.0 を 2026-10-15 に公開した（拡張機能 0.6.0: タブを切り替えて戻っても ref を保つ。
サーバーと SDK は振る舞いを変えず、拡張機能に合わせて minor を上げた）。

kiari は `chrome-bridge-sdk>=0.5,<0.6`。SDK はサーバーの minor が自分と同じことを確かめるので、
8765 で 0.6 系のサーバー（`uv tool` の `chrome-bridge-mcp` 0.6.0。Mac と G-GEAR は 2026-10-15 に上げた）が
動いていると、kiari の chrome の道具は `IncompatibleServerError` で失敗する。サーバーが動いていなければ、
kiari は自分の環境の 0.5 系を managed で起こすので動く。Spirits Garden の body が持つ Dart のサーバー（0.5.2）とも組める。

## やること

- [ ] `pyproject.toml` の制約を `chrome-bridge-sdk>=0.6,<0.7` にし、lock を更新してテストを通す
- [ ] 0.6 系のサーバーを動かした状態で、chrome の道具を 1 回通す
- [ ] リリース（PyPI）と `uv tool` の更新。公開はオーナーの承認を得てから
