from xently.core.loading import _find_registered_app_name, _import_module, _pluck_classes

from xauth.accounts import DEFAULT_AUTH_APP_LABEL
from xauth.internal_settings import AUTH_APP_LABEL

__all__ = ["class_loader"]


def class_loader(module_label, classnames, module_prefix):
    """
    Dynamically import a list of classes from the given module.

    This works by looking up a matching app from the app registry,
    against the passed module label. If the requested class can't be found in
    the matching module, then we attempt to import it from the corresponding
    xauth app, and if that fails, then the corresponding Oscar core app.

    Args:
        module_label (str): Module label comprising the app label and the
            module name, separated by a dot.  For example, 'catalogue.forms'.
        classnames (list<str>): Name of the classes to be imported.
        module_prefix (str):

    Returns:
        The requested class object or ``None`` if it can't be found

    Raises:

        AppNotFoundError: If no app is found in ``INSTALLED_APPS`` that matches
            the passed module label.

        ImportError: If the attempted import of a class raises an
            ``ImportError``, it is re-raised
    """

    if "." not in module_label:
        # Importing from top-level modules is not supported, e.g.
        raise ValueError("Importing from top-level modules is not supported")

    # returns depends on what is set in `settings.INSTALLED_APPS`
    app_name = _find_registered_app_name(module_label)
    if app_name.startswith(f"{module_prefix}."):
        # The entry is obviously an xauth one, we don't import again
        local_module = None
    else:
        # Attempt to import the class(es) from the dependant project's module i.e. assumes an override
        local_module = _import_module(".".join(app_name.split(".") + module_label.split(".")[1:]), classnames)

    # First look in xauth
    xauth_module = _import_module(f"xauth.{module_label.replace(AUTH_APP_LABEL, DEFAULT_AUTH_APP_LABEL)}", classnames)

    if xauth_module is local_module is None:
        # This intentionally doesn't raise an ImportError, because ImportError
        # can get masked in complex circular import scenarios.
        raise ModuleNotFoundError(
            f"The module with label '{module_label}' could not be imported. This either"
            "means that it indeed does not exist, or you might have a problem"
            " with a circular import."
        )

    # return imported classes, giving preference to ones from the local package
    return _pluck_classes([local_module, xauth_module], classnames)
