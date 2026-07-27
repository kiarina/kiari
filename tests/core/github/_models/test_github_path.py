from kiari.core.github import GitHubPathSpec


def test_from_string(tmp_path) -> None:
    github_path = GitHubPathSpec.from_string(
        "@kiarina/kiarina-python/docs/@develop?include=*.txt,*.md&exclude=*.json"
    )

    assert github_path.username == "kiarina"
    assert github_path.repo == "kiarina-python"
    assert github_path.file_path == "docs/"
    assert github_path.commit_hash == "develop"
    assert github_path.include_patterns == ["*.txt", "*.md"]
    assert github_path.exclude_patterns == ["*.json"]

    print("__str__:", str(github_path))

    assert github_path.is_dir is True
    assert github_path.dir_path == "docs"

    print(f"blob_view_url: {github_path.blob_view_url}")
    print(f"raw_content_url: {github_path.raw_content_url}")
    print(f"trees_api_url: {github_path.trees_api_url}")
    print(f"cache_path: {github_path.get_cache_path(tmp_path)}")

    assert github_path.get_commit_hash() == "develop"
