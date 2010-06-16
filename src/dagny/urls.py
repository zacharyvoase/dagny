# -*- coding: utf-8 -*-

from django.conf.urls.defaults import include, patterns, url

__all__ = ['resource']


def resource(resource_name, id=r'\d+', actions=None):
    
    """
    Helper for connecting to resources from your URLconf.
    
    Basic Usage:
    
        from django.conf.urls.defaults import *
        from dagny.urls import resource
        
        urlpatterns = patterns('',
            (r'^users/', resource('myapp.resources.User'))
        )
    
    Remember not to terminate the regex with a `$` character; `resource()`
    actually builds and `include()`s a sub-URLconf, and terminating the regex
    will prevent it from matching anything but the index.
    
    `resource()` supports 4 basic types of URI (shown here with the trailing
    slash, which is Django’s default behavior):
    
        Path                Action
        ---------------------------
        /items/             index
        /items/new/         new
        /items/<id>/        show
        /items/<id>/edit/   edit
    
    In your resource definitions there are usually 7 standard actions, however,
    since routing in Django is independent of the request method, `resource()`
    only acknowledges these four. Note that if a request is received for an
    undefined action, your `Resource` will return the appropriate 404 or 405
    response, regardless of what is defined in your URLconf.
    
    You can restrict the generated patterns by passing the `actions` keyword
    argument to `resource()`:
    
        urlpatterns = patterns('',
            (r'^items/', resource('myapp.resources.Item', actions=('index', 'show')))
        )
    
    The `<id>` parameter mentioned above can also be customized; by default it
    is just a regex pattern which looks for one or more digits (`r'\d+'`), but
    you could use slugs instead by passing an appropriate `id` keyword argument:
    
        urlpatterns = patterns('',
            (r'^items/', resource('myapp.resources.Item', id=r'[\w\-_]+'))
        )
    
    This is where the `actions` parameter becomes useful; if you're using slugs,
    you might want to use a different `new` URI, otherwise you'd need to check
    that no object had a slug of `'new'`.
    """
    
    action_patterns = {
        'index': r'^$',
        'new': r'^new/$',
        'show': r'^(' + id + r')/$',
        'edit': r'^(' + id + r')/edit/$'
    }
    
    if actions is None:
        actions = ('index', 'new', 'show', 'edit')
    
    args = []
    for action in actions:
        args.append(url(action_patterns[action], resource_name, {'action': action}))
    return include(patterns('', *args))
