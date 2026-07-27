from kiarina.i18n import I18n


class ChatModelSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.chat_model"):
    description: str = (
        "Change the chat model.\n\n"
        "  [cyan]/chat_model[/cyan]                "
        "Select a model interactively\n"
        "  [cyan]/chat_model[/cyan] [yellow]<model_name>[/yellow]   "
        "Switch to the specified model directly"
    )
    no_available_models: str = "No available models"
    select_prompt: str = "Select a chat model:"
    selection_cancelled: str = "Chat model selection cancelled"
    model_not_found: str = "Chat model not found: {model_name}"
    model_updated: str = "Chat model updated: {model_name}"
