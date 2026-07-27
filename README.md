# kiari

[English](README.md) | [Japanese](README.ja.md)

`kiari` is a CLI tool for developing and experimenting with qualia-oriented LLM agents.

## Installation

```sh
pip install kiari
```

## Usage

Start the interactive console:

```sh
kiari
```

Run a one-shot batch prompt:

```sh
kiari "hello"
```

Manage profiles:

```sh
kiari profile list
kiari profile new
kiari profile use
```

Generate an image with the built-in `image_generate` tool:

```sh
kiari -t image_generate "Generate an illustration of a cat reading a book"
```

Generate a video with the built-in `video_predict` tool:

```sh
kiari -t video_predict "Generate a short video of a cat playing with a ball"
```

Search the web with the built-in `web` tool:

```sh
kiari -t web "Search the web for the latest Python release"
```

Operate connected Chrome profiles with the built-in `chrome` tool:

```sh
kiari -t chrome "List Chrome tabs, select example.com, and summarize its current page"
```

The Chrome tool requires Chrome Bridge 0.4.x. Install and connect its Chrome extension;
the SDK reuses or starts the loopback server automatically. Each tool action acquires and
releases its own exclusive Chrome Bridge session.

To run the real SDK/extension integration test, connect Chrome Bridge and run:

```sh
make chrome_test
```

The test opens and closes only its own loopback fixture tab. It is marked `costly` and is
skipped by the normal test suite.

See [Chrome Tool and Chrome Bridge](docs/concepts/chrome-tool-and-bridge.md) for session,
target/ref, error, ownership, and SDK update semantics.

## FastAPI Mode

Start an automatically reloading development server:

```sh
kiari fastapi --chat-model openai
```

Run multiple production-style workers without reload:

```sh
kiari fastapi --fastapi-workers 4 --fastapi-path /agent
```

The service exposes `GET /health` and streams agent events as NDJSON from
`POST /` (or the configured path):

```sh
curl -N http://localhost:8000/ \
  -H 'Content-Type: application/json' \
  -d '{"text":"hello"}'
```

Authentication defaults to `none`. Configure Bearer authentication before exposing the
server to an untrusted network, for example with
`--fastapi-authenticator 'bearer?api_key=secret'` or the corresponding component config.
Request `files` are resolved by the server; they are not uploaded by this API.

## Streamlit Mode

Start the browser chat UI:

```sh
kiari streamlit --chat-model openai --history-repository local
```

The default `browser-session` authenticator isolates data for the lifetime of one browser
session. For durable multi-user identity, configure Streamlit OIDC in
`.streamlit/secrets.toml` and start with `--streamlit-authenticator oidc` (or
`oidc?provider=google` for a named provider). Secrets stay in Streamlit configuration and
are not copied into kiari profiles or startup payloads.

Each user creates and selects globally unique agent IDs in the sidebar. Agent IDs accept
letters, digits, `.`, `_`, and `-`. Deleting an agent removes its registered identity and
History; generated files and caches are retained.

The sidebar can apply per-session YAML overrides for agent, tool, workflow, prompt, chat,
and speech options. Runtime-wide settings such as profiles, plugins, repositories,
authentication, loggers, and server options remain fixed at startup.

## Watch Mode

Watch file changes:

```sh
kiari watch "file?paths=.&include_patterns=*.md"
```

Watch Pub/Sub:

```sh
kiari ext pubsub create-topic --project-id kiarina --topic-id tmp
kiari ext pubsub create-subscription --project-id kiarina --topic-id tmp --subscription-id tmp
kiari watch "pubsub?project_id=kiarina&subscription_id=tmp"
kiari ext pubsub publish-message --project-id kiarina --topic-id tmp --attribute hoge=fuga "hello"
```

Watch Realtime Database:

```sh
DATABASE_URL=https://kiarina-python.firebaseio.com/
kiari watch "rtdb?database_url=$DATABASE_URL&path=/posts/kiarina"
kiari ext rtdb set --database-url $DATABASE_URL --path /posts/kiarina '{"message":"hello"}'
kiari ext rtdb get --database-url $DATABASE_URL --path /posts/kiarina
kiari ext rtdb watch --database-url $DATABASE_URL --path /posts/kiarina
```

Watch Slack:

```sh
CHANNEL_ID=C077QKNDCUR
kiari watch "slack?"
kiari watch --watch-handler slack "slack?"
kiari ext slack post-message --channel $CHANNEL_ID "hello"
kiari ext -v slack get-channel-messages --channel $CHANNEL_ID --limit 1
kiari ext slack watch-channel --channel $CHANNEL_ID
```

## Development

```sh
mise run setup
mise run ci
```
