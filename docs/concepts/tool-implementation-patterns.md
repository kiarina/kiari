# Tool Implementation Patterns

この文書は、`kiari/impl/tool_impl/` に組み込みツールを実装するときの構成と、
次の 2 つの実装パターンの使い分けを説明します。

- 1 つのツールで 1 つの機能を提供する単機能型
- 1 つのツールで関連する複数のアクションを提供する複数アクション型

`@tool`、`ToolContext`、`ToolOutputLike` など、依存パッケージ側の API は
[Tools (kiarina-agi-tool)](kiarina-python/tools.md) を参照してください。

## 共通構造

どちらのパターンも、ツール package は次の責務に分けます。

```text
kiari/impl/tool_impl/<tool_name>/
├── __init__.py
├── _i18n.py
├── _models/
│   └── <tool_name>.py
└── _schemas/
    └── <tool_name>_schema.py
```

| 場所 | 責務 |
| --- | --- |
| `__init__.py` | ツールクラスを公開する façade |
| `_i18n.py` | 結果メッセージとエラーメッセージ |
| `_models/<tool_name>.py` | `@tool` を付けた実行関数 |
| `_schemas/<tool_name>_schema.py` | モデルへ公開する説明、引数、型、既定値 |

`@tool(tool_schema=...)` は関数を `BaseTool` のサブクラスへ変換します。実行時には
tool call の引数が Pydantic schema で検証され、その全フィールドが同名の keyword
argument として実行関数へ渡されます。そのため、schema のフィールドと実行関数の引数は、
名前、受け入れる型、既定値を対応させます。実行時情報が必要なツールは、実行関数の先頭に
`ctx: ToolContext` を置きます。

## Schema は LLM に対する API 契約

> **重要:** schema クラスの docstring と各フィールドの `Field.description` は、LLM に渡す
> tool 情報に含まれます。これらは開発者向けの補足コメントではなく、LLM がツールを選び、
> 引数を組み立てるための API 契約です。**実装詳細ではなく、LLM がツールを使うために必要な
> 情報だけを、短く分かりやすく記述します。**

`BaseTool.to_tool_info()` は schema クラスの docstring をツール全体の description に使い、
各フィールドの型、既定値、`Field.description` を含む schema を tool 情報へ変換します。
LLM はツールの Python 関数本体、operation、i18n メッセージを読めません。したがって、
LLM の判断に必要な情報を実装コードだけに書いても伝わりません。

schema クラスの docstring には、次の情報を簡潔に含めます。

- ツールが何をするものか
- どのような状況で使うか
- 複数アクション型では、すべてのアクションで何ができるかと、代表的な使用パターン
- 選択を誤りやすい類似ツールや、重要な制約があれば、その違いと制約

各 `Field.description` には、LLM がその値を生成するために必要な情報を含めます。

- 値の意味と期待する形式
- 単位、範囲、列挙値、基準位置などの制約
- 必須か任意か。複数アクション型では、どのアクションで必要か
- 既定値や `-1`、空文字列などの sentinel が意味すること
- 他フィールドとの関係や、同時に指定する必要がある条件

フィールド名や型注釈だけで意味が明らかだと仮定せず、LLM が tool 情報だけを読んで
「いつ呼ぶか」「どの値を渡すか」を判断できる記述にします。ただし、情報量が多ければよい
わけではありません。内部クラス名、利用ライブラリ、dispatch 方法、処理手順など、LLM の
ツール利用に不要な実装詳細は含めません。説明の各文が LLM のツール選択または引数生成に
必要かを基準に、不要な記述を削ります。

戻り値は用途に応じて `str`、`Content`、`ToolMessage` などの `ToolOutputLike` を使います。
テキストだけなら `str`、ファイルを添付するなら `Content` が基本です。想定内の実行失敗を
失敗した tool message として返す場合は `ToolError` を送出します。一方、ファイルが
見つからない場合にモデルへ再試行を促すなど、正常なツール応答として扱う既存ツールも
あります。呼び出し側が失敗として扱うべきかを基準に、同種の既存ツールと揃えてください。

実装したツールは次の箇所にも接続します。

1. `kiari/core/runtime/_helpers/setup_runtime.py` の `_register_tools()` に、公開 façade を指す
   import path を preset として登録する。
2. `tests/impl/tool_impl/<tool_name>/` に実装ツリーをミラーしたテストを置く。

登録名、preset のキー、tool call の名前、package 名は原則として同じ snake_case 名にします。
Python の公開クラス名は既存ツールに合わせて PascalCase にします。

## パターン 1: 単機能型

代表例は `audio_file_view` です。ツールが表す操作が 1 つなので、公開 schema のフィールドを
実行関数が直接受け取り、そのまま処理します。

```text
audio_file_view/
├── __init__.py
├── _i18n.py
├── _models/
│   └── audio_file_view.py
└── _schemas/
    └── audio_file_view_schema.py
```

構造の要点は次のとおりです。

```python
class AudioFileViewSchema(BaseModel):
    """View an audio file."""

    uri_or_file_path: str = Field(description="...")
    start_time: float = Field(default=0.0, description="...")
    end_time: float = Field(default=-1.0, description="...")


@tool(tool_schema=AudioFileViewSchema)
async def AudioFileView(
    ctx: ToolContext,
    uri_or_file_path: str,
    start_time: float = 0.0,
    end_time: float = -1.0,
) -> Content:
    ...
```

処理が長くなっても、それだけを理由に複数アクション型へ変える必要はありません。1 つの操作を
構成する内部処理は、同じ `_models/` 内の private 関数や `_utils/`、`_services/` へ分離できます。
`video_predict` は、待機、出力ファイル作成、後始末を private 関数へ分けながら、公開上は
1 つの動画生成機能を保っている例です。

### 単機能型を選ぶ目安

- モデルから見た目的が 1 つである。
- 入力項目の大半が常に同じ操作に使われる。
- 独立した `action` 名を導入しても選択の意味が増えない。
- 実行結果とエラーの流れが 1 系統である。

`audio_file_view`、`image_file_view`、`pdf_file_view`、`text_file_view`、
`video_file_view`、`image_generate`、`video_predict`、`change_directory` がこの型です。

## パターン 2: 複数アクション型

代表例は `gui` です。`keyboard_press`、`mouse_move`、`screenshot` など、同じ GUI 操作領域に
属するアクションを 1 つの `gui` ツールとして公開します。共通構造に `_types/action.py` と
`_operations/` が加わります。

```text
gui/
├── __init__.py
├── _i18n.py
├── _models/
│   └── gui.py
├── _operations/
│   ├── keyboard_press.py
│   ├── mouse_move.py
│   └── ...
├── _schemas/
│   └── gui_schema.py
└── _types/
    └── action.py
```

### 1. アクション集合を `Literal` で定義する

```python
Action = Literal[
    "keyboard_press",
    "mouse_move",
    "screenshot",
]
```

`action` は自由な `str` にせず、schema と dispatch table が共有する閉じた型にします。
これにより、不明なアクションは dispatch 前の Pydantic 検証で拒否され、モデルにも選択肢が
列挙されます。

### 2. 1 つの schema に共通入力を定義する

```python
class GuiSchema(BaseModel):
    """Tool for understanding and operating the GUI."""

    action: Action = Field(description="...")
    key: str = Field(default="", description="For keyboard_press action")
    x: int = Field(default=-1, description="For mouse actions")
    y: int = Field(default=-1, description="For mouse actions")
```

複数アクション型では、docstring が長くなりすぎると、LLM が重要な情報を見つけにくくなります。
docstring には全アクションについて「何ができるか」を一行程度で示し、よく使う代表的な
tool call を使用パターンとして提示します。すべての引数の説明や、似た例の網羅は不要です。

`action` の description にはアクションの選択肢と各アクションで必要になる主な引数をまとめ、
各フィールドの `Field.description` には、そのフィールドを使うアクションと値の条件を
記述します。これにより、ツール全体の説明を簡潔に保ちながら、引数生成に必要な詳細を
フィールド側で伝えられます。

現在の複数アクション型は discriminated union ではなく、全アクションの入力を合わせた
共通 schema を使います。そのため、特定アクションだけで必須になるフィールドには既定値を
設定し、各 operation で条件を検証します。たとえば `keyboard_press` の `key` が空なら
`ToolError` を送出します。

### 3. operation のインターフェースを揃える

各 operation は、検証済みの引数を個別の keyword arguments ではなく同じ schema instance
として受け取ります。

```python
async def keyboard_press(ctx: ToolContext, args: GuiSchema) -> str:
    if not args.key:
        raise ToolError("...")
    ...
```

operation には、アクション固有の入力検証と処理を置きます。別アクションの分岐や、ツール全体に
共通する後処理は置きません。この境界にすると、operation 単位で依存関係とテスト対象を
限定できます。

### 4. entry point は組み立てと dispatch を担当する

```python
_OPERATIONS: dict[
    Action,
    Callable[[ToolContext, GuiSchema], Awaitable[str]],
] = {
    "keyboard_press": keyboard_press,
    "mouse_move": mouse_move,
    "screenshot": screenshot,
}


@tool(tool_schema=GuiSchema)
async def Gui(ctx: ToolContext, action: Action, ...) -> Content:
    args = GuiSchema(action=action, ...)
    output = await _OPERATIONS[action](ctx, args)
    ...
```

entry point は、schema と対応する関数引数を受け、operation 用の schema instance を再構築し、
`_OPERATIONS` で dispatch します。`gui` では、dispatch 後に全モニターのスクリーンショットを
作成して `Content` に添付します。このように全アクションへ適用する後処理は entry point に
置きます。共通前処理も同じ考え方です。

operation の戻り値が異なる場合は、`subprocess` のように dispatch table と entry point の
戻り値を union にできます。戻り値の差が大きくなり、共通処理もほとんどなくなった場合は、
別ツールへ分割した方が schema と実装が明確にならないか再検討します。

### 複数アクション型を選ぶ目安

- アクションが同じ利用目的、バックエンド、状態、または後処理を共有する。
- モデルにとって、1 つのツールを選んだ後に `action` を選ぶ方が自然である。
- アクション集合を 1 つの schema で簡潔に説明できる。
- operation ごとに分割すると、entry point が dispatch と共通処理だけになる。

`chrome`、`gui`、`web`、`subprocess`、`text_file_edit` がこの型です。`chrome` は各 operation が入力を検証してから Chrome Bridge の exclusive session を開き、action 終了時に必ず lease を解放します。Chrome 固有の target/ref、ownership、error、test の規約は [Chrome Tool and Chrome Bridge](chrome-tool-and-bridge.md) を参照してください。

反対に、名前が関連しているだけで、権限、失敗時の扱い、入力、出力、ライフサイクルが大きく
異なる機能は、別ツールにします。共通 schema の任意フィールドが増えすぎる、アクション間の
条件分岐が operation の外へ漏れる、モデル向け説明が長く曖昧になる場合も分割の兆候です。

## テスト方針

テストは `BaseTool.run()` または `run_tool()` を通し、デコレータが作る実際のツール境界を
含めて確認します。ツールを直接生成するテストでは、実行前に登録名と同じ `tool.name` を
設定します。

単機能型では、少なくとも次を確認します。

- 正常入力のテキスト、ファイルなどの出力
- 入力 schema の既定値を使う経路
- 見つからない、型が違うなど主要な失敗・再試行経路

複数アクション型では、さらに次を確認します。

- `Action` に列挙した各アクションが正しい operation を呼ぶ
- アクション固有の必須引数がない場合に tool message が失敗する
- 全アクション共通の前後処理
- 共有 singleton や外部サービスを mock したときの呼び出し引数

`Action`、schema の説明、実行関数の signature、`_OPERATIONS` のキーは同時に更新します。
型注釈だけでは dispatch table の網羅性は保証されないため、新しいアクションのテストを
追加し、登録漏れを実行経路で検出します。

## 新しいツールを追加する手順

1. モデルから見た目的と入力を整理し、単機能型か複数アクション型かを選ぶ。
2. package と公開 façade、i18n、schema、`@tool` entry point を作る。
3. 複数アクション型では `Action`、operation、typed dispatch table を作る。
4. schema と実行関数の全フィールドを対応させる。
5. 想定内の失敗を正常応答にするか `ToolError` にするか決める。
6. `_register_tools()` に preset を追加する。
7. 実際のツール実行境界を通るテストを追加する。
8. schema クラスの docstring とすべての `Field.description` を、LLM に実際に渡る API 契約として
   レビューする。LLM が tool 情報だけから、利用場面、アクション、必須引数、値の形式・単位・制約、
   既定値や sentinel の意味を判断できることを確認する。複数アクション型では、docstring が
   全アクションの能力と代表的な使用パターンを簡潔に示し、不要な実装詳細や冗長な例を
   含んでいないことも確認する。
