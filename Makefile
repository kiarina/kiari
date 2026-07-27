.PHONY: init list update upgrade clean format lint check test chrome_test build publish ci
.DEFAULT_GOAL := check
#--------------------------------------------------
init:
	mise run setup
list:
	uv pip list
update:
	uv sync --all-packages --all-extras --all-groups
	uv pip list --outdated
upgrade:
	uv sync --upgrade --all-packages --all-extras --all-groups
clean:
	mise run clean
#--------------------------------------------------
download-test-assets:
	mise run test-assets:download
download-test-settings:
	mise run test-settings:download --force
upload-test-settings:
	mise run test-settings:upload .env test_settings.yaml
#--------------------------------------------------
format:
	mise run format
lint:
	mise run lint
test:
	mise run test
chrome_test:
	mise run test --costly --path tests/impl/tool_impl/chrome
build:
	mise run build
publish:
	mise run publish
#--------------------------------------------------
check:
	mise run format
	mise run lint
ci:
	mise run ci
