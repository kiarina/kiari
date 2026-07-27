from kiarina.i18n import I18n


class PluginI18n(I18n, scope="kiari.core.plugin"):
    missing_dependency_title: str = "Missing dependency: {missing}"
    please_install: str = "Please install:"
    install_command: str = "pip install {missing}"
