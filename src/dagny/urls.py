# -*- coding: utf-8 -*-

from django.conf.urls.defaults import include, patterns, url

__all__ = ['resource']


def resources(resource_name, id=r'\d+', actions=None, name=None):
    
    """
    Helper for connecting to resource collections from your URLconf.
    
    Basic Usage:
    
        from django.conf.urls.defaults import *
        from dagny.urls import resources
        
        urlpatterns = patterns('',
            (r'^users/', resources('myapp.resources.User', name='User'))
        )
    
    Remember not to terminate the regex with a `$` character; `resources()`
    actually builds and `include()`s a sub-URLconf, and terminating the regex
    will prevent it from matching anything but the index.
    
    You also need to pass in the full identifier of your `Resource`, even if you
    specified a common prefix in the call to `patterns()`.
    
    The `name` parameter affects how you’ll do URL reversing; see the section
    below on reversing for in-depth information.
    
    `resources()` generates 4 basic types of URI:
    
        Path                Action
        ---------------------------
        /items/             index
        /items/new/         new
        /items/<id>/        show
        /items/<id>/edit/   edit
    
    In your resource definitions there are usually 7 standard actions, however,
    since routing in Django is independent of the request method, `resources()`
    only acknowledges these four. Note that if a request is received for an
    undefined action, your `Resource` will return the appropriate 404 or 405
    response, regardless of what is defined in your URLconf.
    
    You can restrict the generated patterns by passing the `actions` keyword
    argument to `resources()`:
    
        urlpatterns = patterns('',
            (r'^items/', resources('myapp.resources.Item', actions=('index', 'show')))
        )
    
    The `<id>` parameter mentioned above can also be customized; by default it
    is just a regex pattern which looks for one or more digits (`r'\d+'`), but
    you could use slugs instead by passing an appropriate `id` keyword argument:
    
        urlpatterns = patterns('',
            (r'^items/', resources('myapp.resources.Item', id=r'[\w\-_]+'))
        )
    
    This is where the `actions` parameter becomes useful; if you're using slugs,
    you might want to use a different `new` URI, otherwise you'd need to check
    that no object had a slug of `'new'`.
    
    
    ## Reversing
    
    `resources()` names all of the URLs it generates, which makes it easy for
    you to use Django's existing helpers and templatetags for forms and links.
    By default, the names are just the full identifier of your `Resource`, and
    the particular action, separated by a hash. For example:
    
        class User(models.Model):
            # ...
            
            @models.permalink
            def get_absolute_url(self):
                return ('myapp.resources.User#show', self.id)
    
    Or in templates:
    
        <form method="post" action="{% url myapp.resources.User#show user.id %}">
            ...
        </form>
        
        <a href="{% url myapp.resources.User#new %}">Sign Up</a>
    
    If you want to use shorter identifiers, just pass the `name` keyword
    argument to `resources()`:
    
        urlpatterns = patterns('',
            (r'^users/', resources('myapp.resources.User', name='User'))
        )
    
    And now you can just use that as the prefix:
    
        <a href="{% url User#new %}">Sign Up</a>
    
    """
    
    action_patterns = {
        'index': r'^$',
        'new': r'^new/$',
        'show': r'^(' + id + r')/$',
        'edit': r'^(' + id + r')/edit/$'
    }
    
    if actions is None:
        actions = ('index', 'new', 'show', 'edit')
    
    if name is None:
        name = resource_name
    
    args = []
    for action in actions:
        args.append(url(action_patterns[action], resource_name,
                        kwargs={'action': action},
                        name=("%s#%s" % (name, action))))
    return include(patterns('', *args))


def resource(resource_name, actions=None, name=None):
    
    """
    Helper for connecting to singular resources from your URLconf.
    
    Usage is very similar to `resources()`:
    
        from django.conf.urls.defaults import *
        from dagny.urls import resource
        
        urlpatterns = patterns('',
            (r'^account/', resource('myapp.resources.User'))
        )
    
    `resource()` only generates 3 types of URI:
    
        Path            Action
        ----------------------
        /items/         show
        /items/new/     new
        /items/edit/    edit
    
    As with `resources()`, you can pass the `actions` keyword argument to
    restrict the generated URIs:
    
        urlpatterns = patterns('',
            (r'^account/', resource('myapp.resources.User', actions=('show',)))
        )
    
    The `name` parameter works in exactly the same way as with `resources()`:
    
        # urls.py:
        
        urlpatterns = patterns('',
            (r'^account/', resource('myapp.resources.User', name="Account"))
        )
        
        # account/show.html
        
        <a href="{% url Account#edit %}">Edit Account</a>
    
    """
    
    action_patterns = {
        'show': r'^$',
        'new': r'^new/$',
        'edit': r'^edit/$',
    }
    
    if actions is None:
        actions = ('show', 'new', 'edit')
    
    if name is None:
        name = resource_name
    
    args = []
    for args in actions:
        args.append(url(action_patterns[action], resource_name,
                        kwargs={'action': action},
                        name=("%s#%s" % (name, action))))
    return include(patterns('', *args))
