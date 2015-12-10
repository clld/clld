from __future__ import unicode_literals, print_function
import json

import requests
from sqlalchemy.orm import joinedload
from six.moves.urllib.parse import quote_plus
from six import text_type
from clldutils.misc import slug

from clld.scripts.util import confirm
from clld.db.models import common
from clld.db.meta import DBSession
from clld.db.util import page_query


API_URL = 'https://archive.org/advancedsearch.php?fl[]=creator&fl[]=identifier&' \
    'fl[]=title&fl[]=year&sort[]=&sort[]=&sort[]=&rows=5&page=1&output=json&callback&' \
    'save=yes&q='


def ia_func(command, args, sources=None):  # pragma: no cover
    def words(s):
        return set(slug(s.strip(), remove_whitespace=False).split())

    log = args.log
    count = 0

    if not sources:
        sources = DBSession.query(common.Source)\
            .order_by(common.Source.id)\
            .options(joinedload(common.Source.data))
    else:
        if callable(sources):
            sources = sources()

    i = 0
    for i, source in enumerate(page_query(sources, verbose=True, commit=True)):
        filepath = args.data_file('ia', 'source%s.json' % source.id)

        if command in ['verify', 'update']:
            if filepath.exists():
                with open(filepath) as fp:
                    try:
                        data = json.load(fp)
                    except ValueError:
                        continue
                if not data['response']['numFound']:
                    continue
                item = data['response']['docs'][0]
            else:
                continue

        if command == 'verify':
            stitle = source.description or source.title or source.booktitle
            needs_check = False
            year = text_type(item.get('year', ''))
            if not year or year != slug(source.year or ''):
                needs_check = True
            twords = words(stitle)
            iwords = words(item['title'])
            if twords == iwords \
                    or (len(iwords) > 2 and iwords.issubset(twords))\
                    or (len(twords) > 2 and twords.issubset(iwords)):
                needs_check = False
            if needs_check:
                log.info('------- %s -> %s' % (source.id, item['identifier']))
                log.info(item['title'])
                log.info(stitle)
                log.info(item.get('year'))
                log.info(source.year)
                log.info(item['creator'])
                log.info(source.author)
                if not confirm('Are the records the same?'):
                    log.warn('---- removing ----')
                    with open(filepath, 'w') as fp:
                        json.dump({"response": {'numFound': 0}}, fp)
        elif command == 'update':
            source.update_jsondata(internetarchive_id=item['identifier'])
            count += 1
        elif command == 'download':
            if source.author and (source.title or source.booktitle):
                title = source.title or source.booktitle
                if filepath.exists():
                    continue
                q = quote_plus(b'creator:"%s" AND title:"%s"' % (
                    source.author.split(',')[0].encode('utf8'), title.encode('utf8')))

                count += 1
                r = requests.get(API_URL + q, headers={'accept': 'application/json'})
                log.info('%s - %s' % (r.status_code, r.url))
                if r.status_code == 200:
                    with open(filepath, 'w') as fp:
                        fp.write(r.text.encode('utf8'))
                elif r.status_code == 403:
                    log.warn("limit reached")
                    break
    if command == 'update':
        log.info('assigned internet archive identifiers for %s out of %s sources'
                 % (count, i))
    elif command == 'download':
        log.info('queried internet archive for %s sources' % count)
