__version__ = "1.0.3"


def get_next_version(old_version: str = __version__):
    f, s, l = tuple([int(n) for n in old_version.split('.', 3)])
    l = l + 1 if l <= 9 else l
    if l > 9:
        l = 0
        s = s + 1 if s <= 9 else s
        if s > 9:
            s = 0
            f = f + 1

    return f'{f}.{s}.{l}'
