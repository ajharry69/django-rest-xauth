from xently.core.loading import _find_registered_app_name, _import_module, _pluck_classes


def class_loader(module_label, classnames, module_prefix):
    """
    Dynamically import a list of classes from the given module.

    This works by looking up a matching app from the app registry,
    against the passed module label.  If the requested class can't be found in
    the matching module, then we attempt to import it from the corresponding
    xauth app, and if that fails, then the corresponding Oscar core app.

    Args:
        module_label (str): Module label comprising the app label and the
            module name, separated by a dot.  For example, 'catalogue.forms'.
        classname (str): Name of the class to be imported.

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

    # First look in xauth
    xauth_module = _import_module(f"xauth.{module_label}", classnames)
    # if nothing is there, then look in Oscar itself
    # e.g. 'oscar.apps.dashboard.catalogue.forms'
    oscar_module = _import_module(f"{module_prefix}.{module_label}", classnames)

    # returns e.g. 'oscar.apps.dashboard.catalogue',
    # 'yourproject.apps.dashboard.catalogue' or 'dashboard.catalogue',
    # depending on what is set in INSTALLED_APPS
    app_name = _find_registered_app_name(module_label)
    if app_name.startswith(f"{module_prefix}."):
        # The entry is obviously an Oscar one, we don't import again
        local_module = None
    else:
        # Attempt to import the classes from the local module
        # e.g. 'yourproject.dashboard.catalogue.forms'
        local_module_label = ".".join(app_name.split(".") + module_label.split(".")[1:])
        local_module = _import_module(local_module_label, classnames)

    if xauth_module is oscar_module is local_module is None:
        # This intentionally doesn't raise an ImportError, because ImportError
        # can get masked in complex circular import scenarios.
        raise ModuleNotFoundError(
            f"The module with label '{module_label}' could not be imported. This either"
            "means that it indeed does not exist, or you might have a problem"
            " with a circular import."
        )

    # return imported classes, giving preference to ones from the local package
    return _pluck_classes([local_module, xauth_module, oscar_module], classnames)
