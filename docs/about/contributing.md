# Contributing to django-rest-xauth

An introduction to contributing to the django-rest-xauth project.

The django-rest-xauth project welcomes, and depends, on contributions from developers and
users in the open source community. Contributions can be made in a number of
ways, a few examples are:

- Code patches via pull requests
- Documentation improvements
- Bug reports and patch reviews

## Code of Conduct

Everyone interacting in the django-rest-xauth project's codebase, issue trackers, chat
rooms, and mailing lists is expected to follow the [PyPA Code of Conduct].

## Reporting an Issue

Please include as much detail as you can. Let us know your platform and django-rest-xauth
version. If the problem is visual (for example a theme or design issue) please
add a screenshot and if you get an error please include the full error and
traceback.

## Running the tests

To run the tests, it is recommended that you use [tox].

Install Tox using [pip] by running the command `pip install tox`.
Then the test suite can be run for django-rest-xauth by running the command `tox` in the
root of your django-rest-xauth repository.

It will attempt to run the tests against all of the Python versions we
support. So don't be concerned if you are missing some and they fail. The rest
will be verified by [Travis] when you submit a pull request.

## Submitting Pull Requests

Once you are happy with your changes or you are ready for some feedback, push
it to your fork and send a pull request. For a change to be accepted it will
most likely need to have tests and documentation if it is a new feature.

[virtualenv]: https://virtualenv.pypa.io/en/latest/user_guide.html
[pip]: https://pip.pypa.io/en/stable/
[tox]: https://tox.readthedocs.io/en/latest/
[travis]: https://travis-ci.com/repositories
[PyPA Code of Conduct]: https://www.pypa.io/en/latest/code-of-conduct/
