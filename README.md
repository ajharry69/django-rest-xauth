# Welcome to django-rest-xauth

[![CI](https://github.com/ajharry69/django-rest-xauth/actions/workflows/django.yml/badge.svg)](https://github.com/ajharry69/django-rest-xauth/actions/workflows/django.yml)
[![Coverage Status](https://coveralls.io/repos/github/ajharry69/django-rest-xauth/badge.svg?branch=master)](https://coveralls.io/github/ajharry69/django-rest-xauth?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/5c5b5dbbe3204b3bae605d6b81800d73)](https://www.codacy.com/manual/ajharry69/django-rest-xauth?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ajharry69/django-rest-xauth&amp;utm_campaign=Badge_Grade)
[![Documentation Status](https://readthedocs.org/projects/django-rest-xauth/badge/?version=latest)](https://django-rest-xauth.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/django-rest-xauth.svg)](https://badge.fury.io/py/django-rest-xauth)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-rest-xauth)

## Documentation

Go [here](docs/index.md#quick-start) for quick-setup/start or [here][documentation-url] for full documentation.

## Test run

### With docker

Run `make build_image_and_run`. You can then go to [http://localhost:8000/](http://localhost:8000/) and signin to the
default user account using `superuser@example.com` as email and `demoproject` as password.

To add extra options to the default `docker run` command, use `docker_run_options` in the make command
e.g. `make run docker_run_options='-v ./:/app/'`.

### Without docker

After setting up all requirements using `make dev`, start django server as you would in any project
e.g. `./manage.py runserver`.

## Contributing

Please be sure to review [contributing guidelines](docs/about/contributing.md) to learn how to help the project.

[jwt-url]: https://jwt.io/

[django-customizing-user-model-url]: https://docs.djangoproject.com/en/dev/topics/auth/customizing/

[documentation-url]: https://django-rest-xauth.readthedocs.io/en/latest/
