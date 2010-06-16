# -*- coding: utf-8 -*-

"""Helpers and global mappings for content negotiation."""

import mimetypes

from webob.acceptparse import MIMEAccept

__all__ = ['MIMETYPES', 'match_accept']


MIMETYPES = {
    'rss': 'application/rss+xml',
    'json': 'application/json',
    'rdf_xml': 'application/rdf+xml',
}


for ext, mimetype in mimetypes.types_map.iteritems():
    ext = ext.lstrip(".").replace(".", "_")  # .tar.bz2 => tar_bz2
    MIMETYPES[ext] = mimetype
del ext, mimetype  # Clean up


def match_accept(accept_header, renderers, default='html'):
    """Return the best match for an Accept header and a list of renderers."""
    
    mapping = dict([(MIMETYPES[renderer], renderer) for renderer in renderers])
    return mapping.get(MIMEAccept("Accept", accept_header).best_match(mapping.keys()), default)
