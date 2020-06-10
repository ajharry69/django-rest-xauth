__version__ = "1.0.4"


def get_next_version(old_version: str = __version__, max_minor: int = 9, max_patch: int = 9):
    """
    Calculates and returns the next version of a software that uses **major**.**minor**.**patch**
     from `old_version`.
     For example, given `max_minor` & `max_patch` = 9 and `old_version` is values listed on the
     left(below) then the values provided on the right side(after the = sign) of every value
     would be returned as the next version
     "1.0.0" = "1.0.1"
     "1.0.9" = "1.1.0"
     "1.9.9" = "2.0.0"
     "10.9.9" = "11.0.0"
    """
    major, minor, patch = tuple([int(n) for n in old_version.split('.', 3)])
    patch = patch + 1 if patch <= max_patch else patch
    if patch > max_patch:
        patch = 0
        minor = minor + 1 if minor <= max_minor else minor
        if minor > max_minor:
            minor = 0
            major = major + 1

    return f'{major}.{minor}.{patch}'
