mwtextextractor
===================
mwtextextractor extracts simple body text from MediaWiki wikitext by stripping off templates, html tags, tables, headers, etc.
The extracted text can be used for word counting.


Example:

.. code-block:: python

    from mwtextextractor import get_body_text
    print get_body_text('Lorem {{ipsum}} dolor')
