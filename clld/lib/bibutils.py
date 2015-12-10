"""
python interface to bibutils.

.. seealso:: http://sourceforge.net/p/bibutils/home/Bibutils/
"""
from subprocess import Popen, PIPE

from clldutils.misc import encoded


FORMATS = ['bib', 'end', 'ris']


def pipe(cmd, input_):
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    return proc.communicate(encoded(input_))[0]


def convert(string, from_, to_=None):
    assert from_ in FORMATS and (to_ is None or to_ in FORMATS)

    res = pipe('%s2xml -i utf8 -o utf8' % from_, encoded(string))
    if to_:
        res = pipe('xml2%s -i utf8 -o utf8' % to_, res)
    return res.decode('utf8')
