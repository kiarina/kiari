from rich_click.utils import OptionGroupDict

STREAMLIT_OPTION_GROUP: OptionGroupDict = {
    "name": "Streamlit",
    "options": [
        "--streamlit-host",
        "--streamlit-port",
        "--streamlit-headless",
        "--streamlit-title",
        "--streamlit-icon",
        "--streamlit-layout",
        "--streamlit-handler",
        "--streamlit-authenticator",
    ],
}
