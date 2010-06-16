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
    'xhtml': 'application/xhtml+xml',
    'xml': 'application/xml',
}


# Load all extension => mimetype mappings from `mimetypes` stdlib module.
for ext, mimetype in mimetypes.types_map.iteritems():
    shortcode = ext.lstrip(".").replace(".", "_")  # .tar.bz2 => tar_bz2
    MIMETYPES.setdefault(shortcode, mimetype)
del ext, shortcode, mimetype  # Clean up


def match_accept(header, shortcodes):
    
    """
    Match an Accept header against a list of shortcodes, in order of preference.
    
    A few examples:
    
        >>> header = "application/xml,application/xhtml+xml,text/html"
        
        >>> match_accept(header, ['html', 'json', 'xml'])
        ['html', 'xml']
        
        >>> header2 = "application/json,application/xml"
        
        >>> match_accept(header2, ['html', 'json', 'xml'])
        ['json', 'xml']
        
        >>> match_accept(header2, ['html', 'xml', 'json'])
        ['xml', 'json']
    
    """
    
    server_types = map(MIMETYPES.__getitem__, shortcodes)
    client_types = MIMEAccept("Accept", header).best_matches()
    matches = []
    for mimetype in server_types:
        if mimetype in client_types:
            matches.append(mimetype)
    
    return map(shortcodes.__getitem__, map(server_types.index, matches))
