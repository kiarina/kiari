from kiarina.i18n import I18n


class GitHubI18n(I18n, scope="kiari.core.github_trusted"):
    security_warning_title: str = "Security Warning: Untrusted Source"
    security_warning_intro: str = "You are about to load a file from an untrusted source:"
    security_warning_source: str = "Source: @{username}/{repo}/{file_path}"
    security_warning_url: str = "URL: {url}"
    security_warning_access: str = "This file will have full access to your system."
    security_warning_trust: str = "Only proceed if you trust this source."
    trust_prompt: str = "Do you trust this source?"
    trust_choice_yes: str = "Yes, load this file once"
    trust_choice_always: str = "Always trust all files from @{username}"
    trust_choice_no: str = "No, cancel execution"
    trust_prompt_requires_tty: str = (
        "Interactive trust confirmation requires a TTY. "
        "Use --github-trusted-username or --github-skip-trust-verification."
    )
    execution_cancelled: str = "Execution cancelled"
    added_to_trusted: str = "Added @{username} to trusted sources"
