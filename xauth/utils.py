def is_valid_str(string, length: int = 1) -> bool:
    """
    Checks for `string`'s null(not None and length) status

    :param string: str checked for validity
    :param length: minimum length `string` should have
    :return: True if `string` is of `length`
    """
    return string is not None and isinstance(string, str) and len(string) > length - 1
