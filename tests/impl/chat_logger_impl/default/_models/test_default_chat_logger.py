from kiarina.agi.message import AIMessage, AIMessageChunk, ToolCallChunk

from kiari.impl.chat_logger_impl.default import DefaultChatLogger


def test_invoke(run_context) -> None:
    chat_logger = DefaultChatLogger()
    chat_logger.log_chat_invoke_start(run_context)
    chat_logger.log_chat_invoke_end(AIMessage.create("test"), run_context)


def test_stream(run_context) -> None:
    run_context.metadata["chat_model"] = "mock"
    run_context.metadata["token_count"] = 123

    chat_logger = DefaultChatLogger()

    with chat_logger.log_chat_stream(run_context):
        s = "hello"

        for i in range(len(s)):
            chat_logger.log_chat_stream_chunk(AIMessageChunk.create(s[i]))

        chat_logger.log_chat_stream_chunk(
            AIMessageChunk(
                tool_call_chunks=[
                    ToolCallChunk(
                        name="test_tool",
                        args='{"arg1": "value1"}',
                    )
                ]
            )
        )
