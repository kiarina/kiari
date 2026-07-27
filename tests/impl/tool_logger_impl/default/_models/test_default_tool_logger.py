from kiarina.agi.content import Content
from kiarina.agi.display_content import FileDisplayContent, TextDisplayContent
from kiarina.agi.file_info import FileInfo
from kiarina.agi.message import ToolCall, ToolMessage

from kiari.impl.tool_logger_impl.default import DefaultToolLogger


def test_default_tool_logger(run_context, text_file_info, image_file_info: FileInfo) -> None:
    tool_logger = DefaultToolLogger()

    tool_call = ToolCall(
        id="1",
        name="subprocess",
        args={
            "action": "run",
            "reason": "test",
            "expect": "ok",
            "argv": ["echo", "hello"],
        },
    )

    tool_message = ToolMessage(
        contents=[
            Content(
                text="Hello",
                files=[text_file_info, image_file_info],
            )
        ],
        tool_name=tool_call.name,
        tool_call_id=tool_call.id,
        return_direct=True,
        artifact={"my_artifact": "This is an artifact."},
        metadata={
            "my_metadata_1": "This is metadata 1.",
            "my_metadata_2": "This is metadata 2.",
        },
        display_contents=[
            TextDisplayContent(text="This is display content."),
            FileDisplayContent(
                mime_type=image_file_info.mime_type,
                uri_or_file_path=image_file_info.uri_or_file_path,
                display_name="sample image",
            ),
        ],
    )

    tool_logger.log_tool_start(tool_call, run_context.with_metadata(tool=tool_call.name))
    tool_logger.log_tool_end(tool_message, run_context)

    assert True
