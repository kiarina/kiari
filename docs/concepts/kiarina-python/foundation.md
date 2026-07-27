# Foundation: Context, Data Model, Chat (kiarina-agi-base / data / data-builder / file / text)

エージェントを支える横断的な基盤。kiari のコードで最も頻繁に import されるのはこの層です
（`message`, `event`, `run_context`, `content`, `history` など）。

前提バージョンは [overview.md](overview.md#documented-versions) を参照。

## kiarina-agi-base — 実行コンテキストと観測

| モジュール | 内容 |
| --- | --- |
| `kiarina.agi.run_context` | `RunContext`: 実行 ID・タイムゾーン等の実行時コンテキスト。`RunContextSettings` で構成 |
| `kiarina.agi.cost_recorder` | コスト集計の抽象（`BaseCostRecorder` + registry）。kiari 実装例: なし（標準実装 `cost_recorder_impl/` を利用） |
| `kiarina.agi.cost_logger` | コストのロギング抽象。kiari 実装例: `kiari/impl/cost_logger_impl/` |
| `kiarina.agi.cost_record` / `cost_utils` | コストのデータ型と計算 |
| `kiarina.agi.request_logger` | LLM リクエストのロギング抽象 |
| `kiarina.agi.token_utils` | トークン数の見積り・計算 |
| `kiarina.agi.console_utils` | コンソール表示ユーティリティ |
| `kiarina.agi.file_utils` / `image_types` | ファイル・画像の補助型 |

## kiarina-agi-data — データモデル

エージェントが扱うデータの Pydantic モデル群。serialization、estimate、shrink などモデルに
密接な基本操作を持ち、外部入力からの組み立てや複数モデルをまたぐ調整は data-builder が担当。

| モジュール | 内容 |
| --- | --- |
| `kiarina.agi.message` | `Message` / `AIMessage` / `ToolMessage` などメッセージ型 |
| `kiarina.agi.history` | `History`: 会話履歴。永続化の抽象は kiari 側 `kiari/lib/history_repository/` |
| `kiarina.agi.event` | `Event`: agent 実行が流すイベント（ストリーミングの単位） |
| `kiarina.agi.content` / `display_content` | メッセージ内コンテンツと表示用コンテンツ |
| `kiarina.agi.file_info` / `file_info_pool` / `file_bundle` | 添付ファイルのメタデータと束 |
| `kiarina.agi.tool_info` | ツール定義のメタデータ |
| `kiarina.agi.chat_limits` / `chat_estimates` | コンテキスト上限と見積り |
| `kiarina.agi.embedding` | 埋め込みデータ型 |

`History → Event → Message → Content → FileInfo` の所有関係、Event stream と永続化の境界、
FileInfo pool の hydrate / dehydrate は [Data Model and History](data-model-and-history.md) を
参照してください。

`FileInfo` の `pinned`、`inline`、`metadata_only`、`content_only`、`no_merge`、
`group`、`unique_key`、`keep_from_end` は、履歴・上限調整・prompt 変換を変える実行時
ポリシーです。生成経路と各パラメータの意味は
[FileInfo and Data Builder](file-info-and-data-builder.md) を参照してください。

## kiarina-agi-data-builder — データの組み立て

`*_builder`（message / history / event / content / tool_info / file_info）、
`file_factory`、`file_info_loader`、`local_scanner`（ローカルファイル走査）など。
kiari の実行モードが入力（テキスト・添付・ファイル）を History に変換する際に使われます。
利用箇所は `rg 'file_info_loader|event_builder|local_scanner' kiari/` で確認。
`FileInfo` については builder だけでなく、segment normalizer と file adjuster まで一続きで
読む必要があります。詳細は [FileInfo and Data Builder](file-info-and-data-builder.md) を参照。

2.19.0 以降、PDF / video builder は `analysis_enabled=True` のとき、chat model の capability に
応じて内容を選べる `FileBundle` を生成します。PDF は native PDF、page image、抽出 text、video は
native video、timestamp 付き frame、音声 transcript / ambient event を bundle に含め、model が
未対応の media には fallback を使います。既定値は `False` なので、有効化と解像度・frame rate の
指定方法は [FileInfo and Data Builder](file-info-and-data-builder.md) を参照してください。

## kiarina-agi-file — ファイル・キャッシュ・リポジトリ抽象

`file`, `asset_cache`, `asset_repository`, `local_repository`。
添付や生成物の保存・キャッシュに関わるときに見る。

## kiarina-agi-text — チャットモデルとテキスト埋め込み

| モジュール | 内容 |
| --- | --- |
| `kiarina.agi.chat_model` / `chat_provider` | チャット LLM の抽象と provider。`ChatOptions` はここ |
| `kiarina.agi.langchain_chat_provider` | LangChain 経由の provider（Anthropic / OpenAI / Google 等はこれで繋がる） |
| `kiarina.agi.chat_logger` | チャットのロギング抽象。kiari 実装例: `kiari/impl/chat_logger_impl/` |
| `kiarina.agi.text_embedding_model` / `text_embedding_provider` | テキスト埋め込み |

OpenAI provider の cost record は 2.19.0 以降、tiered pricing と prompt cache write cost を
区別して計算します。kiari の cost logger / recorder を変更するときは、入力・出力 token だけを
前提にせず provider が生成する cost record の内訳を保持してください。
