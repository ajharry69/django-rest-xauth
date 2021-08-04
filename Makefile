venv_dir ?= .venv

bin_dir ?= $(venv_dir)/bin/

requirements_txt ?= requirements-dev.txt

port ?= 8000

image_name ?= xauth

options :=

# The following variable can be used like:
# 	1. `make test_options='tests/ --create-db -vv' test` for multiple (space-separated) options.
# 	2. `make test_options=tests/ test` for single option.
# where value(s) passed to `test_options` are valid `py.test` options.
test_options :=

.PHONY: help venv build_image run build_image_and_run install_requirements dev update_repo test test_lint

help: ## Display this help message.
	@echo "Please use \`make <target>\` where <target> is one of"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; \
	{printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'

venv: ## Sets up virtual environment.
	python3 -m venv $(venv_dir)

build_image:
	docker build -t django-rest-xauth:latest .

run:
	docker stop xauth || true
	docker run --rm -dp $(port):8000 --name=$(image_name) django-rest-xauth:latest
	docker exec $(image_name) /bin/sh -c "./manage.py collectstatic --noinput"
	docker exec $(image_name) /bin/sh -c "./manage.py migrate --noinput"
	docker exec $(image_name) /bin/sh -c "./manage.py loaddata fixtures/users.json"

build_image_and_run: build_image run

install_requirements: ## Install python requirements.
	$(bin_dir)pip install -U pip wheel
	$(bin_dir)pip install --use-feature=in-tree-build -Ur $(requirements_txt)
	rm -Rf build
	rm -Rf django_rest_xauth.egg-info

dev: venv install_requirements ## Sets up development environment by installing this project's development dependencies within virtual environment.
	$(bin_dir)pre-commit install --install-hooks

update_repo: ## Pulls and merges latest changes from git's remote repository.
	git pull

test:
	py.test $(test_options)

test_lint:
	$(bin_dir)pre-commit run --all-files --color never