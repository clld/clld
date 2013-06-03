"""
support for reading and writing deimiter-separated value files.
"""


def rows(filename, delimiter='\t'):
    with open(filename, 'r') as fp:
        for line in fp:
            yield [s.strip() for s in line.split(delimiter)]
