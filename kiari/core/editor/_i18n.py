from kiarina.i18n import I18n


class EditorI18n(I18n, scope="kiari.core.editor"):
    validation_failed_prompt: str = "Validation failed. What do you want to do?"
    choice_continue: str = "Continue editing (keep edits)"
    choice_reset: str = "Reset to original and edit"
    choice_abort: str = "Abort"
