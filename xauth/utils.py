from django.apps import apps


def is_model_registered(app_label, model_name):
    try:
        apps.get_registered_model(app_label, model_name)
    except LookupError:
        return False
    else:
        return True
