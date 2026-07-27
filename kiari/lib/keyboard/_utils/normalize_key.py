def normalize_key(key: str) -> str:
    """
    Normalize the input key

    Absorbs errors during LLM tool calls.
    """
    if key == "cmd":
        return "command"

    return key
