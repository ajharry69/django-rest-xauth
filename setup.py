import os
import re
import shutil
import sys

import setuptools


from xauth import get_next_version


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, "__init__.py"), "rb") as init_py:
        src = init_py.read().decode("utf-8")
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", src).group(1), src


def update_version(package):
    old_version, src = get_version(package)
    new_version = get_next_version(old_version=old_version)
    new_file_content = re.sub("__version__ = ['\"]([^'\"]+)['\"]", f'__version__ = "{new_version}"', src)
    with open(os.path.join(package, "__init__.py"), "wb") as init_py:
        init_py.write(bytes(new_file_content, encoding="utf-8"))


version, _ = get_version("xauth")

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    long_description = readme.read()

if sys.argv[-1] == "publish":
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist bdist_wheel")
    if os.system("twine check dist/*"):
        print("twine check failed. Packages might be outdated.")
        print("Try using `pip install -U twine wheel`.\nExiting.")
        sys.exit()
    if re.match('^-([t]|-test)$', sys.argv[-2]):
        # uploads test package
        os.system('twine upload --repository testpypi dist/*')
    else:
        # uploads production package
        os.system("twine upload dist/*")
    print("You probably want to also tag the version now:")
    print(" git tag -a {0} -m 'version {0}'".format(version))
    print(" git push --tags")
    update_version('xauth')
    shutil.rmtree('dist')
    shutil.rmtree('build')
    shutil.rmtree('django_rest_xauth.egg-info')
    sys.exit()

setuptools.setup(
    name="django-rest-xauth",
    version=version,
    author="Orinda Harrison",
    author_email="mitch@xently.com",
    description="A custom user-model based package with features ranging from JWT and Basic authentication to REST API"
                " end-points for signup, signin, email verification, password resetting and account activation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords='django django-rest-framework jwt-bearer-tokens basic-authentication encryption-decryption authorization '
             'authentication',
    url="https://github.com/ajharry69/django-rest-xauth",
    packages=setuptools.find_packages(
        exclude=("*.tests", "*.tests.*", "tests.*", "tests", "djangorestxauth", "demo",),
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires='>=3.6',
    install_requires=[
        'djangorestframework',
        'django-templated-email',
        'jwcrypto',
        'timeago',
    ],
    include_package_data=True,
    zip_safe=False,
    project_urls={
        'Source': 'https://github.com/ajharry69/django-rest-xauth',
    },
)
