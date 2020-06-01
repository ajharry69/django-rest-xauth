from enum import Enum, auto


class AuthProvider(Enum):
    EMAIL = auto()
    GOOGLE = auto()
    FACEBOOK = auto()
    TWITTER = auto()
    GITHUB = auto()
    APPLE = auto()
    PHONE = auto()


class PasswordResetType(Enum):
    CHANGE = auto()
    RESET = auto()
