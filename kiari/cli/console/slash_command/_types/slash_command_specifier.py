from .slash_command_name import SlashCommandName

type SlashCommandSpecifier = SlashCommandName | str
"""
A string in the form of "{SlashCommandName}?{ConfigString}"

Examples:
- "help"
- "help?key1=value1&key2=value2"
"""
