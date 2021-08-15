import logging
from os.path import dirname, exists, join
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from xauth.accounts import DEFAULT_AUTH_APP_LABEL


def create_file(filepath, content=""):
    with open(filepath, "w") as f:
        f.write(content)


def create_local_app_folder(local_app_path):
    if exists(local_app_path):
        raise ValueError(f"There is already a '{local_app_path}' folder! Aborting!")

    def subfolders(path):
        """
        Decompose a path string into a list of subfolders

        Eg Convert 'apps/dashboard/ranges' into
           ['apps', 'apps/dashboard', 'apps/dashboard/ranges']
        """
        folders = []
        while path not in ("/", ""):
            folders.append(path)
            path = dirname(path)
        folders.reverse()
        return folders

    for folder in subfolders(local_app_path):
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        init_path = folder / "__init__.py"
        if not init_path.exists():
            create_file(init_path)


class Command(BaseCommand):
    help = "Create a local version of xauth app so it can easily be customised"

    def add_arguments(self, parser):
        parser.add_argument("target_path", help="The path to copy the files to")

    def handle(self, *args, **options):
        # Use a stdout logger
        logger = logging.getLogger(__name__)
        stream = logging.StreamHandler(self.stdout)
        logger.addHandler(stream)
        logger.setLevel(logging.DEBUG)

        target_path = options["target_path"]
        try:
            # Remove trailing slash from folder path
            local_app_folder_path = target_path.rstrip("/")

            # Check if local_folder_path is current folder
            if local_app_folder_path == ".":
                local_app_folder_path = "xauth"  # Use as default app folder name

            # Create folder
            self.stdout.write(self.style.WARNING(f"Creating package {local_app_folder_path}..."))
            create_local_app_folder(local_app_folder_path)

            # Create minimum app files
            self.stdout.write(self.style.WARNING("Creating admin.py..."))
            create_file(join(local_app_folder_path, "admin.py"), "from xauth.accounts.admin import *  # noqa\n")

            self.stdout.write(self.style.WARNING("Creating app config..."))
            local_app_name = local_app_folder_path.lstrip("/").replace("/", ".")
            create_file(
                join(local_app_folder_path, "apps.py"),
                f"""from django import apps


class AppConfig(apps.AppConfig):
    name = "{local_app_name}"
""",
            )

            self.stdout.write(self.style.WARNING("Creating models.py..."))
            create_file(
                join(local_app_folder_path, "models.py"),
                f"""from django.db import models

from xauth.accounts import abstract_models


class User(abstract_models.AbstractUser):
    email = models.EmailField(db_index=True, max_length=150, blank=False, unique=True)

    EMAIL_FIELD = "email"  # returned by `self.get_email_field_name()`

    USERNAME_FIELD = EMAIL_FIELD

    @classmethod
    def serializable_fields(cls):
        return ("email",) + super().serializable_fields()

    @classmethod
    def admin_panel_fields(cls):
        return ("email",) + super().admin_panel_fields()


# TODO: Add other model overrides here...

from xauth.accounts.models import *  # noqa isort:skip
""",
            )

            self.stdout.write(self.style.WARNING("Creating migrations folder..."))
            local_migrations_folder_path = Path(join(local_app_folder_path, "migrations"))
            local_migrations_folder_path.mkdir(parents=True, exist_ok=True)
            create_file(local_migrations_folder_path / "__init__.py")

            # Final step needs to be done by hand
            app_label = local_app_name.rsplit(".", 1)[-1]
            message = f"""
Make the following changes in your project's settings module - where you've defined django settings:
    1. Add "{local_app_name}.apps.AppConfig" and "rest_framework" to INSTALLED_APPS.
    2. Add 'xauth.settings import *  # noqa'
    """
            if app_label != DEFAULT_AUTH_APP_LABEL:
                message += f"""3. Add 'AUTH_USER_MODEL = "{app_label}.User"'
    4. Add 'XAUTH_AUTH_APP_LABEL = \"{app_label}\"'"""
            self.stdout.write(self.style.SUCCESS(message))
        except Exception as e:
            raise CommandError(str(e))
