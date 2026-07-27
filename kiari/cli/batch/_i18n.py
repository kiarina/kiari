from kiarina.i18n import I18n


class BatchI18n(I18n, scope="kiari.cli.batch"):
    command_help: str = "Run LLM agents once with text, attachments, stdin, or an exec file."
    texts_help: str = (
        "Input text to send as the user message. Multiple values are joined with "
        "spaces and combined with Markdown body text or stdin input when provided."
    )
    attachments_help: str = (
        "File, URI, GitHub source, or file pattern to attach to the user message. Repeatable."
    )
    stdin_help: str = (
        "Read standard input and use it as either a human message body or a system message."
    )
    batch_handler_help: str = (
        "BatchHandler name or config string to run. "
        "Example: 'vanilla' or 'vanilla?key1=value1&key2=value2'."
    )
    output_text_help: str = (
        "Print only the final event text to stdout after the batch run finishes."
    )
