from .web_name import WebName

type WebSpecifier = WebName | str
"""
A string in the form of "{WebName}?{ConfigString}"

Examples:
- "kiapi"
- "kiapi?kiapi_base_url=http://127.0.0.1:8500"
"""
