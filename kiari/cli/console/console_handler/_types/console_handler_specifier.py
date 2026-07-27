from .console_handler_name import ConsoleHandlerName

type ConsoleHandlerSpecifier = ConsoleHandlerName | str
"""
A string in the form of "{ConsoleHandlerName}?{ConfigString}"

Examples:
- "vanilla"
- "vanilla?key1=value1&key2=value2"
"""
