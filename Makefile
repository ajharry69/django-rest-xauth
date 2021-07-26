venv_dir ?= .venv

bin_dir ?= $(venv_dir)/bin/

requirements_txt ?= requirements.txt

options :=

# The following variable can be used like:
# 	1. `make test_options='tests/ --create-db -vv' test` for multiple (space-separated) options.
# 	2. `make test_options=tests/ test` for single option.
# where value(s) passed to `test_options` are valid `py.test` options.
test_options :=

.PHONY: help venv dev update_repo test

help: ## Display this help message.
	@echo "Please use \`make <target>\` where <target> is one of"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; \
	{printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'

venv: ## Sets up virtual environment.
	python3 -m venv $(venv_dir)

install_requirements: ## Install python requirements.
	$(bin_dir)pip install -U pip wheel
	$(bin_dir)pip install --use-feature=in-tree-build -Ur $(requirements_txt)
	rm -R build || true
	rm -R django_rest_xauth.egg-info || true

dev: venv install_requirements ## Sets up development environment by installing this project's development dependencies within virtual environment.
	$(bin_dir)pre-commit install --install-hooks

update_repo: ## Pulls and merges latest changes from git's remote repository.
	git pull

test:
	py.test $(test_options)

test_lint:
	$(bin_dir)pre-commit run --all-files --color never