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

import string
from lxml.html import fromstring
from mwtemplates import preprocessToXml


def condition_for_lxml(text):
    r"""
    lxml does not not tackle short tags with unquoted arguments very well.
    As an example, this is a piece of wikitext which is often encountered:

    >>> txt = '<root><ref name=XYZ/>Some text</root>'

    Let's see how lxml parses it:

    >>> from __future__ import print_function
    >>> from lxml.html import fromstring
    >>> from lxml.etree import tounicode
    >>> print(tounicode(fromstring(txt)))
    <root><ref name="XYZ/">Some text</ref></root>

    Not quite as expected. Add a space before the slash, and we get the expected result:
    >>> txt = '<root><ref name=XYZ />Some text</root>'
    >>> print(tounicode(fromstring(txt)))
    <root><ref name="XYZ"/>Some text</root>

    Therefore we should condition the text before sending it to lxml
    """
    text = re.sub(r'<ref ([^>]+)=\s?([^"\s]+)/>', r'<ref \1=\2 />', text)

    def evaluate(match):
        return '<math>%s</math>' % match.group(1).replace('<', '&lt;')
    text = re.sub(r'<math>(.*?)</math>', evaluate, text)

    # ... but <'s are also sometimes used outside math tags. Since they
    # are often followed by a space or a number, escaping anyone not
    # followed by a letter should help a bit.
    text = re.sub(r'<(?![a-zA-Z/])', '&lt;', text)

    # strip whitespace at beginning of lines, as it makes finding tables harder
    text = re.sub(r'\n[\s]+', r'\n', text)

    return text


def get_body_text(text):

    xml = preprocessToXml(text)
    xml = xml.replace('&lt;', '<').replace('&gt;', '>')

    root = fromstring(condition_for_lxml(xml))

    out = ''
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
            if depth == 0:
                buf.append(out[cpos:current['pos']])
                logger.warning('Found |}, but no table was open.')
            else:
                depth -= 1
            cpos = current['pos'] + 2

    if depth == 0:
        buf.append(out[cpos:])
    out = ''.join(buf)

    out = re.sub(r'==[=]*', '', out)                                 # drop header markers (but keep header text)
    out = re.sub(r"''[']*", '', out)                                 # drop bold/italic markers (but keep text)

    # Note that re.sub has no flags support in python2.6, which is why we use re.compile
    rec1 = re.compile(r'^(?:#|\*).*?$', flags=re.MULTILINE)          # drop lists altogether
    out = rec1.sub('', out)

    out = re.sub(r'\[\[Kategori:[^\]]+\]\]', '', out)                # drop categories
    out = re.sub(r'(?<!\[)\[(?!\[)[^ ]+ [^\]]+\]', '', out)          # drop external links
    out = re.sub(r'\[\[(?:[^:|\]]+\|)?([^:\]]+)\]\]', '\\1', out)    # wikilinks as text, '[[Artikkel 1|artikkelen]]' -> 'artikkelen'
    out = re.sub(r'\[\[(?:Fil|File|Image|Bilde):[^\]]+\|([^\]]+)\]\]', '\\1', out)  # image descriptions only
    out = re.sub(r'\[\[[A-Za-z\-]+:[^\]]+\]\]', '', out)             # drop interwikis

    exclude = set(string.punctuation)
    out = ' '.join(ch for ch in out.split() if ch not in exclude)
    return out
