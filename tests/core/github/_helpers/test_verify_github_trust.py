# TODO: kiari 公開後にテストデータを改善する
import pytest

from kiari.core.github import (
    GitHubPathSpec,
    github_trusted_source_store,
    settings_manager,
    verify_github_trust,
)


@pytest.fixture(autouse=True)
def cleanup_github_settings():
    yield
    settings_manager.cli_args = {}


@pytest.fixture(autouse=True)
async def cleanup_github_trusted_source_store():
    yield
    await github_trusted_source_store.delete()


async def test_github_path_pattern() -> None:
    settings_manager.cli_args = {"trusted_usernames": ["kiarina"]}
    trusted = await verify_github_trust("@kiarina/kiarina-python/README.md")
    assert trusted is True


async def test_github_path_spec() -> None:
    settings_manager.cli_args = {"trusted_usernames": ["kiarina"]}
    trusted = await verify_github_trust(
        GitHubPathSpec.from_string("@kiarina/kiarina-python/README.md")
    )
    assert trusted is True


async def test_skip() -> None:
    settings_manager.cli_args = {"skip_trust_verification": True}
    trusted = await verify_github_trust("@kiarina/kiarina-python/README.md")
    assert trusted is True


async def test_trusted() -> None:
    settings_manager.cli_args = {"trusted_usernames": ["spirits-garden"]}
    await github_trusted_source_store.save(["spirits-garden"])

    trusted = await verify_github_trust("@spirits-garden/spirits-garden/README.md")
    assert trusted is True


async def test_no(monkeypatch: pytest.MonkeyPatch) -> None:
    async def mock_ask_trust_prompt(username: str) -> str:
        return "no"

    monkeypatch.setattr(
        "kiari.core.github._helpers.verify_github_trust._ask_trust_prompt",
        mock_ask_trust_prompt,
    )

    trusted = await verify_github_trust("@spirits-garden/spirits-garden/README.md")
    assert trusted is False


async def test_no_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "kiari.core.github._helpers.verify_github_trust.has_interactive_tty",
        lambda: False,
    )

    trusted = await verify_github_trust("@spirits-garden/spirits-garden/README.md")
    assert trusted is False


async def test_always(monkeypatch: pytest.MonkeyPatch) -> None:

    async def mock_ask_trust_prompt(username: str) -> str:
        return "always"

    monkeypatch.setattr(
        "kiari.core.github._helpers.verify_github_trust._ask_trust_prompt",
        mock_ask_trust_prompt,
    )

    trusted = await verify_github_trust("@spirits-garden/spirits-garden/README.md")
    assert trusted is True

    # should be saved to trusted sources
    trusted = await verify_github_trust("@spirits-garden/spirits-garden/README.md")
    assert trusted is True
