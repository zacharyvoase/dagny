# -*- coding: utf-8 -*-

from django.conf.urls.defaults import include, patterns, url


def resource(resource_name, id=r'\d+', actions=None):
    action_patterns = {
        'index': r'^$',
        'new': r'^new/$',
        'show': r'^(' + id + r')/$',
        'edit': r'^(' + id + r')/edit$'
    }
    
    if actions is None:
        actions = ('index', 'new', 'show', 'edit')
    
    args = []
    for action in actions:
        args.append(url(action_patterns[action], resource_name, {'action': action}))
    return include(patterns('', *args))
