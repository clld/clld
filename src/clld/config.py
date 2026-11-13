import pathlib
import functools
import configparser
from typing import Any


def get_config(p: str | pathlib.Path) -> dict[str, Any]:
    """Read a config file.

    :return: dict of ('section.option', value) pairs.
    """
    cfg = {}
    parser = configparser.ConfigParser()
    parser.read_file(pathlib.Path(p).open(encoding='utf8'))

    for section in parser.sections():
        getters = {
            'int': functools.partial(parser.getint, section),
            'boolean': functools.partial(parser.getboolean, section),
            'float': functools.partial(parser.getfloat, section),
            'list': lambda option: parser.get(section, option).split(),
        }
        default = functools.partial(parser.get, section)
        for option in parser.options(section):
            type_ = option.rpartition('_')[2] if '_' in option else None
            value = getters.get(type_, default)(option)
            cfg[f'{section}.{option}'] = value

    return cfg
