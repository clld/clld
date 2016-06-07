"""Functionality to gather information about iso-639-3 codes from sil.org."""
# http://www-01.sil.org/iso639-3/iso-639-3_20130531.tab
#
# Id      char(3) NOT NULL,  -- The three-letter 639-3 identifier
# Part2B  char(3) NULL,      -- Equivalent 639-2 identifier of the bibliographic
#                               applications
#                            -- code set, if there is one
# Part2T  char(3) NULL,      -- Equivalent 639-2 identifier of the terminology
#                               applications code
#                            -- set, if there is one
# Part1   char(2) NULL,      -- Equivalent 639-1 identifier, if there is one
# Scope   char(1) NOT NULL,  -- I(ndividual), M(acrolanguage), S(pecial)
# Type    char(1) NOT NULL,  -- A(ncient), C(onstructed),
#                            -- E(xtinct), H(istorical), L(iving), S(pecial)
# Ref_Name   varchar(150) NOT NULL,   -- Reference language name
# Comment    varchar(150) NULL)       -- Comment relating to one or more of the columns
#
#
# http://www.sil.org/iso639-3/iso-639-3_Name_Index_20130520.tab
#
# Id             char(3)     NOT NULL,  -- The three-letter 639-3 identifier
# Print_Name     varchar(75) NOT NULL,  -- One of the names associated with this
#                                       -- identifier
# Inverted_Name  varchar(75) NOT NULL)  -- The inverted form of this Print_Name form
#
#
# http://www-01.sil.org/iso639-3/iso-639-3-macrolanguages_20130314.tab
#
# M_Id      char(3) NOT NULL,   -- The identifier for a macrolanguage
# I_Id      char(3) NOT NULL,   -- The identifier for an individual language
#                               -- that is a member of the macrolanguage
# I_Status  char(1) NOT NULL)   -- A (active) or R (retired) indicating the
#                               -- status of the individual code element
#
#
# http://www-01.sil.org/iso639-3/iso-639-3_Retirements_20130531.tab
#
# Id          char(3)      NOT NULL,     -- The three-letter 639-3 identifier
# Ref_Name    varchar(150) NOT NULL,     -- reference name of language
# Ret_Reason  char(1)      NOT NULL,     -- code for retirement: C (change),
#                                        -- D (duplicate), N (non-existent), S (split),
#                                        -- M (merge)
# Change_To   char(3)      NULL,         -- in the cases of C, D, and M, the identifier
#                                        -- to which all instances of this Id should be
#                                        -- changed
# Ret_Remedy  varchar(300) NULL,         -- The instructions for updating an instance
#                                        -- of the retired (split) identifier
# Effective   date         NOT NULL)     -- The date the retirement became effective
#
import re

import requests
from bs4 import BeautifulSoup as bs

from clldutils import dsv


TAB_NAME_PATTERN = re.compile(
    'iso-639-3(?P<name>_Name_Index|\-macrolanguages|_Retirements)'
    '?(_(?P<date>[0-9]{8}))?\.tab$')


def get(path):
    """Retrieve a resource from the sil site and return it's representation."""
    return requests.get("http://www-01.sil.org/iso639-3/" + path).content


def get_taburls():
    """Retrieve the current (date-stamped) file names for download files from sil."""
    soup = bs(get('download.asp'), "html5lib")
    name_map = {
        None: 'codes',
        '_Name_Index': 'names',
        '-macrolanguages': 'macrolanguages',
        '_Retirements': 'retired',
    }
    res = {}
    for a in soup.find_all('a', href=True):
        match = TAB_NAME_PATTERN.match(a['href'])
        if match:
            res[name_map.get(match.group('name'))] = a['href']
    return res


def get_tab(name):
    """Generator for entries in a tab file specified by name."""
    return dsv.reader(
        get(get_taburls()[name]).split('\n'), namedtuples=True, delimiter='\t')


def _text(e):
    return e.text.strip()


def get_documentation(code):
    """Scrape information about a iso 639-3 code from the documentation page."""
    soup = bs(get('documentation.asp?id=' + code), "html5lib")
    assert code in soup.find_all('h1', limit=1)[0].text

    info = {}
    for table in soup.find_all('table'):
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) == 2:
                info[_text(tds[0]).replace(':', '')] = _text(tds[1])
    return info
