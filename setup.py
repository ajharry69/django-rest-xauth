import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-rest-xauth",
    version="1.0.0",
    author="Orinda Harrison",
    author_email="mitch@xently.com",
    description="A custom user-model based package that offers numerous features from JWT and Basic authentication to "
                "REST API end-points for signup, signin, email verification, password resetting and account "
                "activation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords='django django-rest-framework jwt-bearer-tokens basic-authentication encryption-decryption authorization '
             'authentication djangorestframework-jwt',
    url="https://github.com/ajharry69/django-rest-xauth",
    packages=setuptools.find_packages(
        exclude=("*.tests", "*.tests.*", "tests.*", "tests", "djangorestxauth", "api",),
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.0.6",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires='>=3.6',
    install_requires=[
        'django',
        'djangorestframework',
        'jwcrypto',
        'timeago',
    ],
)
