import re


def convert_markdown_to_mrkdwn(markdown: str) -> str:
    text = markdown
    bold_placeholders: list[str] = []

    def preserve_bold(match: re.Match[str]) -> str:
        bold_placeholders.append(f"*{match.group(1)}*")
        return f"@@BOLD_{len(bold_placeholders) - 1}@@"

    text = re.sub(r"\*\*(.+?)\*\*", preserve_bold, text)
    text = re.sub(r"__(.+?)__", preserve_bold, text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"_\1_", text)
    text = re.sub(r"~~(.+?)~~", r"~\1~", text)
    text = re.sub(r"```[\w]*\n(.*?)\n```", r"```\1```", text, flags=re.DOTALL)
    text = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r"<\2|\1>", text)
    text = re.sub(r"^[\-\*] ", "• ", text, flags=re.MULTILINE)

    for index, value in enumerate(bold_placeholders):
        text = text.replace(f"@@BOLD_{index}@@", value)

    return text
