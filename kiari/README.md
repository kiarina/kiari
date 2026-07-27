## watch モード

```sh
# ファイルの変更を監視
kiari watch "file?paths=.&include_patterns=*.md"

# PubSub を監視
kiari ext pubsub create-topic --project-id kiarina --topic-id tmp
kiari ext pubsub create-subscription --project-id kiarina --topic-id tmp --subscription-id tmp
kiari watch "pubsub?project_id=kiarina&subscription_id=tmp"
kiari ext pubsub publish-message --project-id kiarina --topic-id tmp --attribute hoge=fuga "hello"

# Realtime Database を監視
DATABASE_URL=https://kiarina-python.firebaseio.com/
kiari watch "rtdb?database_url=$DATABASE_URL&path=/posts/kiarina"
# - 複数のパスを監視
kiari watch \
"rtdb?database_url=$DATABASE_URL&path=/posts/kiarina" \
"rtdb?database_url=$DATABASE_URL&path=/status/kiarina"
kiari ext rtdb set --database-url $DATABASE_URL --path /posts/kiarina '{"message":"hello"}'
kiari ext rtdb get --database-url $DATABASE_URL --path /posts/kiarina
kiari ext rtdb watch --database-url $DATABASE_URL --path /posts/kiarina

# Slack を監視
CHANNEL_ID=C077QKNDCUR
kiari watch "slack?"
kiari watch --watch-handler slack "slack?"
kiari ext slack post-message --channel $CHANNEL_ID "hello"
kiari ext -v slack get-channel-messages --channel $CHANNEL_ID --limit 1
kiari ext slack watch-channel --channel $CHANNEL_ID
```
