from __future__ import annotations

import typing


class SingletonMeta(type):
    """
    The Singleton class ensures there is always only one instance of a certain class that is globally available.
    This implementation is __init__ signature agnostic.
    """

    _instances: dict[typing.Any, typing.Any] = {}

    def __call__(cls: SingletonMeta, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
