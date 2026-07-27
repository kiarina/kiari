from .finalizer_name import FinalizerName

type FinalizerSpecifier = FinalizerName | str
"""
A string in the form of "{FinalizerName}?{ConfigString}"

Examples:
- "default"
- "my_finalizer?key1=value1&key2=value2"
"""
