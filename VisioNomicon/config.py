import tomllib

from .constants import get_config_dir

CONFIG = {}


def get_config():
    global CONFIG
    try:
        with open(f"{get_config_dir()}config.toml", "rb") as f:
            CONFIG = tomllib.load(f)
    except FileNotFoundError:
        return {}
    return CONFIG
