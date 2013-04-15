try:
    from ConfigParser import ConfigParser
except ImportError:  # pragma: no cover
    from configparser import ConfigParser
import codecs


def get_config(p):
    """Reads a config file.

    :return: dict of ('section.option', value) pairs.
    """
    cfg = {}

    parser = ConfigParser()
    parser.readfp(codecs.open(p, encoding='utf8'))

    for section in parser.sections():
        for option in parser.options(section):
            type_ = option.split('_')[-1] if '_' in option else None
            value = {
                'int': parser.getint,
                'boolean': parser.getboolean,
                'float': parser.getfloat,
            }.get(type_, parser.get)(section, option)
            value = {
                'list': lambda v: v.split(),
            }.get(type_, lambda v: v)(value)
            cfg['{0}.{1}'.format(section, option)] = value

    return cfg
