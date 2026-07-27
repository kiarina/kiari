from .batch_handler_name import BatchHandlerName

type BatchHandlerSpecifier = BatchHandlerName | str
"""
A string in the form of "{BatchHandlerName}?{ConfigString}"

Examples:
- "my_batch_handler"
- "my_preset_handler?key1=value1&key2=value2"
"""
