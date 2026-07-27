from pydantic import BaseModel, Field

from .._types.action import Action


class WebSchema(BaseModel):
    """
    Search the web or fetch a web page as Markdown.

    Supports the following actions:
    - search: Search the web
      Required arguments: query
    - fetch: Fetch a web page as Markdown
      Required arguments: url
    """

    action: Action = Field(
        description=(
            "Web action to execute\n\n"
            '- "search": Search the web (Required arguments: query)\n'
            '- "fetch": Fetch a web page as Markdown (Required arguments: url)'
        ),
    )

    query: str = Field(
        default="",
        description="Search query. (For search action)",
    )

    url: str = Field(
        default="",
        description="URL of the web page to fetch. (For fetch action)",
    )
