from kiarina.i18n import I18n


class StreamlitI18n(I18n, scope="kiari.cli.streamlit"):
    command_help: str = "Run kiari as a Streamlit application."
    host_help: str = "Host address for the Streamlit server."
    port_help: str = "Port for the Streamlit server."
    headless_help: str = "Do not open a browser when the server starts."
    title_help: str = "Streamlit page title."
    icon_help: str = "Streamlit page icon."
    layout_help: str = "Streamlit page layout."
    handler_help: str = "StreamlitHandler name or config string."
    authenticator_help: str = "StreamlitAuthenticator name or config string."
