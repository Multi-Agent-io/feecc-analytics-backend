import typing

import yaml


async def load_yaml(data: str) -> typing.Any:
    return yaml.load(data, Loader=yaml.SafeLoader)
