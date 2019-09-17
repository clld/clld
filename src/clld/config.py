from functools import partial
from configparser import ConfigParser
from pathlib import Path


def get_config(p):
    """Read a config file.

    :return: dict of ('section.option', value) pairs.
    """
    cfg = {}
    parser = ConfigParser()
    parser.read_file(Path(p).open(encoding='utf8'))

    for section in parser.sections():
        getters = {
            'int': partial(parser.getint, section),
            'boolean': partial(parser.getboolean, section),
            'float': partial(parser.getfloat, section),
            'list': lambda option: parser.get(section, option).split(),
        }
        default = partial(parser.get, section)
        for option in parser.options(section):
            type_ = option.rpartition('_')[2] if '_' in option else None
            value = getters.get(type_, default)(option)
            cfg['{0}.{1}'.format(section, option)] = value

    return cfg
