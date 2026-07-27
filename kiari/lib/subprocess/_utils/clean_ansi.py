import re


def clean_ansi(text: str) -> str:
    """
    Remove ANSI escape sequences

    Remove ANSI escape sequences using regular expressions.

    Args:
        text: Text that may contain ANSI escape sequences

    Returns:
        Plain text with ANSI escape sequences removed
    """
    if not text.strip():
        return text

    # ANSI escape sequences (color codes, cursor control, etc.)
    # 1. CSI (Control Sequence Introducer): sequences starting with \x1B[
    # 2. OSC (Operating System Command): sequences starting with \x1B] (hyperlinks, title changes, etc.)
    # 3. Other escape sequences: \x1B + 1 character

    # CSI sequence: ESC [ ... (final character from @ to ~)
    csi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

    # OSC sequence: ESC ] ... BEL(\a) or ESC \ (ST: String Terminator)
    # Note: In case of ST(\x1B\\), \x1B\\ is the string terminator, so it's not included in the OSC content
    osc_escape = re.compile(r"\x1B\][^\a\x1B]*(?:\a|\x1B\\)")

    # Other escape sequences: ESC + 1 character (from @ to _)
    other_escape = re.compile(r"\x1B[@-Z\\-_]")

    # Control characters (0x00-0x1F except tab, 0x7F-0x9F) are also removed
    control_chars = re.compile(r"[\x00-\x08\x0B-\x1F\x7F-\x9F]")

    # Remove escape sequences sequentially
    clean_text = csi_escape.sub("", text)
    clean_text = osc_escape.sub("", clean_text)
    clean_text = other_escape.sub("", clean_text)

    # Remove control characters (but preserve tabs and newlines)
    clean_text = control_chars.sub("", clean_text)

    # Remove multiple consecutive blank lines
    lines = clean_text.split("\n")
    result_lines = []
    prev_empty = False

    for line in lines:
        line = line.rstrip()  # Remove trailing whitespace
        is_empty = not line

        # Keep only one consecutive blank line
        if is_empty and prev_empty:
            continue

        result_lines.append(line)
        prev_empty = is_empty

    # Remove trailing blank lines
    while result_lines and not result_lines[-1]:
        result_lines.pop()

    return "\n".join(result_lines)
