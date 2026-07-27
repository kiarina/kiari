from kiarina.i18n import I18n


class WebI18n(I18n, scope="kiari.impl.tool_impl.web"):
    search_requires_query_error: str = "Error: search action requires query"
    fetch_requires_url_error: str = "Error: fetch action requires url"
