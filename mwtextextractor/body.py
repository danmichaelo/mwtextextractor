# encoding=utf-8
"""
mwtextextractor
Copyright (c) 2012-2013 Dan Michael O. Heggø

Extracts simple :body text from MediaWiki wikitext,
by stripping off templates, html tags, tables, headers, etc.

"""

from __future__ import unicode_literals
import re
import logging
logger = logging.getLogger(__name__)

from lxml.html import fromstring
from mwtemplates import preprocessToXml


def condition_for_soup(text):
    """
    While BeautifulSoup and its parsers are robust, (unknown) tags with
    unquoted arguments seems to be an issue.

    Let's first define a function to make things clearer:
    >>> def f(str):
    >>>     out = ''
    >>>     for tag in BeautifulSoup(str, 'lxml').findAll('body')[0].contents]):
    >>>         out.append(unicode(tag))
    >>>     return ''.join(out)

    Now, here is an unexpected result: the ref-tag is not read as closed and
    continue to eat the remaining text!
    >>> f('<ref name=XYZ/>Mer tekst her')
    <<< u'<ref name="XYZ/">Mer tekst her</ref>'

    Add a space before / and we get the expected result:
    >>> f('<ref name=XYZ />Mer tekst her')
    <<< u'<ref name="XYZ"></ref>Mer tekst her'

    Therefore we should condition the text before sending it to BS
    """
    text = re.sub(r'<ref ([^>]+)=\s?([^"\s]+)/>', r'<ref \1=\2 />', text)

    # strip whitespace at beginning of lines, as it makes finding tables harder
    text = re.sub(r'\n[\s]+', r'\n', text)

    return text


def get_body_text(text):

    xml = preprocessToXml(text)
    xml = xml.replace('&lt;', '<').replace('&gt;', '>')

    root = fromstring(condition_for_soup(xml))

    out = u''
    if root.text:
        out += root.text
    for child in root.iterchildren():
        if child.tail:
            out += child.tail

    # Strip tables
    buf = []
    depth = 0
    cpos = 0
    while True:
        openpos = out.find('{|', cpos)
        closepos = out.find('|}', cpos)
        if openpos == -1 and closepos == -1:
            break
        elif openpos == -1:
            current = {'mark': 'close', 'pos': closepos}
        elif closepos == -1:
            current = {'mark': 'open', 'pos': openpos}
        else:
            if openpos < closepos:
                current = {'mark': 'open', 'pos': openpos}
            else:
                current = {'mark': 'close', 'pos': closepos}

        if current['mark'] == 'open':
            if depth == 0:
                buf.append(out[cpos:current['pos']])
            cpos = current['pos'] + 2
            depth += 1
        else:
            cpos = current['pos'] + 2
            depth -= 1

    if depth == 0:
        buf.append(out[cpos:])
    out = ''.join(buf)

    out = re.sub(r'==[=]*', '', out)                                 # drop header markers (but keep header text)
    out = re.sub(r"''[']*", '', out)                                 # drop bold/italic markers (but keep text)
    out = re.sub(r'^#.*?$', '', out, flags=re.MULTILINE)             # drop lists altogether
    out = re.sub(r'^\*.*?$', '', out, flags=re.MULTILINE)            # drop lists altogether
    out = re.sub(r'\[\[Kategori:[^\]]+\]\]', '', out)                # drop categories
    out = re.sub(r'(?<!\[)\[(?!\[)[^ ]+ [^\]]+\]', '', out)          # drop external links
    out = re.sub(r'\[\[(?:[^:|\]]+\|)?([^:\]]+)\]\]', '\\1', out)    # wikilinks as text, '[[Artikkel 1|artikkelen]]' -> 'artikkelen'
    out = re.sub(r'\[\[(?:Fil|File|Image|Bilde):[^\]]+\|([^\]]+)\]\]', '\\1', out)  # image descriptions only
    out = re.sub(r'\[\[[A-Za-z\-]+:[^\]]+\]\]', '', out)             # drop interwikis

    out = out.strip()
    return out
