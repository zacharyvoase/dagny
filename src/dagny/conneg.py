# -*- coding: utf-8 -*-

"""
Helpers and global mappings for content negotiation.

If you want to define a custom mimetype shortcode, add it to the `MIMETYPES`
dictionary in this module (without the leading '.' character). For example:

    from dagny.conneg import MIMETYPES
    
    MIMETYPES['png'] = 'image/png'
    MIMETYPES['json'] = 'text/javascript'

"""

import mimetypes

from webob.acceptparse import MIMEAccept

__all__ = ['MIMETYPES', 'match_accept']


# Maps renderer shortcodes => mimetypes.
MIMETYPES = {
    'rss': 'application/rss+xml',
    'json': 'application/json',
    'rdf_xml': 'application/rdf+xml',
}


# Load all extension => mimetype mappings from `mimetypes` stdlib module.
for ext, mimetype in mimetypes.types_map.iteritems():
    shortcode = ext.lstrip(".").replace(".", "_")  # .tar.bz2 => tar_bz2
    MIMETYPES[shortcode] = mimetype
del ext, shortcode, mimetype  # Clean up


def match_accept(header, shortcodes, default='html'):
    """Match an Accept header against a list of renderer shortcodes."""
    
    types = map(MIMETYPES.__getitem__, shortcodes)
    match = MIMEAccept("Accept", header).best_match(types)
    if match:
        return shortcodes[types.index(match)]
    return default
