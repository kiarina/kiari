from .._schemas.size import Size

MAX_SCALING_TARGETS = {
    "1:1": Size(1092, 1092),  # 1
    "4:3": Size(1268, 951),  # 1.33
    "3:2": Size(1344, 896),  # 1.5
    "16:9": Size(1456, 819),  # 1.77
    "2:1": Size(1568, 784),  # 2
}
"""
List of maximum scaling target resolutions

- Maximum resolutions that are not resized by Anthropic's Vision API
- Additionally, must be within 1600 tokens
- For more details, see [Anthropic Vision API](https://docs.anthropic.com/en/docs/build-with-claude/vision)
"""
