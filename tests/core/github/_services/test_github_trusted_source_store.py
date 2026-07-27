import pytest

from kiari.core.github import github_trusted_source_store


@pytest.fixture(autouse=True)
async def cleanup_trusted_source_store():
    yield
    await github_trusted_source_store.delete()


async def test_trusted_source_store() -> None:
    usernames = await github_trusted_source_store.load()
    assert usernames == []

    await github_trusted_source_store.save(["hello"])
    usernames = await github_trusted_source_store.load()
    assert set(usernames) == {"hello"}
