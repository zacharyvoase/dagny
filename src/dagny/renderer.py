# -*- coding: utf-8 -*-

from functools import wraps

import odict

from dagny import conneg


class Skip(Exception):
    
    """
    Move on to the next renderer backend.
    
    This exception can be raised by a renderer backend to instruct the
    `Renderer` to ignore the current backend and move on to the next-best one.
    """


class Renderer(object):
    
    """
    Manage a collection of renderer backends, and their execution on an action.
    
    A renderer backend is a callable which accepts an `Action` and a `Resource`
    and returns an instance of `django.http.HttpResponse`. For example:
    
        >>> def render_html(action, resource):
        ...     from django.http import HttpResponse
        ...     return HttpResponse(content="<html>...</html>")
    
    Backends are associated with mimetypes on the `Renderer`, through mimetype
    shortcodes (see `dagny.conneg` for more information on shortcodes). The
    `Renderer` exports a dictionary-like interface for managing these
    associations:
    
        >>> r = Renderer()
        
        >>> r['html'] = render_html
        
        >>> r['html']  # doctest: +ELLIPSIS
        <function render_html at 0x...>
        
        >>> 'html' in r
        True
        
        >>> del r['html']
        
        >>> r['html']
        Traceback (most recent call last):
            ...
        KeyError: 'html'
        
        >>> 'html' in r
        False
    
    A few helpful dictionary methods have also been added, albeit
    underscore-prefixed to prevent naming clashes. Behind the scenes, `Renderer`
    uses [odict](http://pypi.python.org/pypi/odict), which will keep the keys in
    the order they were *first* defined. Here are a few examples:
    
        >>> r['html'] = 1
        >>> r['json'] = 2
        >>> r['xml'] = 3
        
        >>> r._keys()
        ['html', 'json', 'xml']
        
        >>> r._items()
        [('html', 1), ('json', 2), ('xml', 3)]
        
        >>> r._values()
        [1, 2, 3]
    
    This order preservation is useful for ConNeg, since you can define backends
    in order of server preference and the negotiator will consider them
    appropriately. You can push something to the end of the queue by removing
    and then re-adding it:
    
        >>> r['html'] = r._pop('html')
        
        >>> r._keys()
        ['json', 'xml', 'html']
    
    You can also define backends using a handy decorator-based syntax:
    
        >>> @r.html
        ... def render_html_2(action, resource):
        ...     from django.http import HttpResponse
        ...     return HttpResponse(content="<html>...</html>")
        
        >>> r['html'] is render_html_2
        True
    
    Remember that your shortcode *must* be pre-registered with
    `dagny.conneg.MIMETYPES` for this to work, otherwise an `AttributeError`
    will be raised. This also introduces the constraint that your shortcode must
    be a valid Python identifier.
    """
    
    def __init__(self, backends=None):
        if backends is None:
            backends = odict.odict()
        else:
            backends = backends.copy()
        self._backends = backends
    
    def __getattr__(self, shortcode):
        
        """
        Support use of decorator syntax to define new renderer backends.
        
            >>> r = Renderer()
            
            >>> @r.html
            ... def render_html(action, resource):
            ...     return "<html>...</html>"
            
            >>> render_html  # doctest: +ELLIPSIS
            <function render_html at 0x...>
            
            >>> r['html']  # doctest: +ELLIPSIS
            <function render_html at 0x...>
            
            >>> r['html'] is render_html
            True
        
        """
        
        if shortcode not in conneg.MIMETYPES:
            raise AttributeError(shortcode)
        
        def decorate(function):
            self[shortcode] = function
            return function
        return decorate
    
    def __call__(self, action, resource):
        matches = self._match(action, resource)
        
        for shortcode in matches:
            try:
                return self[shortcode](action, resource)
            except Skip:
                continue
        
        return not_acceptable(action, resource)
    
    def _match(self, action, resource):
        """Return all matching shortcodes for a given action and resource."""
        
        matches = []
        
        format_override = resource._format()
        if format_override and (format_override in self._keys()):
            matches.append(format_override)
        
        accept_header = resource.request.META.get('HTTP_ACCEPT')
        if accept_header:
            matches.extend(conneg.match_accept(accept_header, self._keys()))
        
        if (not matches) and ('html' in self):
            matches.append('html')
        
        return matches
    
    def _bind(self, action):
        
        """
        Bind this `Renderer` to an action, returning a `BoundRenderer`.
        
            >>> r = Renderer()
            >>> action = object()
            >>> r['html'] = 1
            
            >>> br = r._bind(action)
            >>> br  # doctest: +ELLIPSIS
            <BoundRenderer on <object object at 0x...>>
        
        Associations should be preserved, albeit on a copied `odict`, so that
        modifications to the `BoundRenderer` do not propagate back to this.
        
            >>> br['html']
            1
            >>> br['html'] = 2
            >>> br['html']
            2
            >>> r['html']
            1
            >>> r['html'] = 3
            >>> r['html']
            3
            >>> br['html']
            2
        
        """
        
        return BoundRenderer(action, backends=self._backends)
    
    def _copy(self):
        return type(self)(backends=self._backends)
    
    ### <meta>
    #
    #   This chunk of code creates several proxy methods going through to
    #   `_backends`. A group of them are underscore-prefixed to prevent naming
    #   clashes with the `__getattr__`-based decorator syntax (so you could
    #   still associate a backend with a shortcode of 'pop', for example).
    
    proxy = lambda meth: property(lambda self: getattr(self._backends, meth))
    
    for method in ('__contains__', '__getitem__', '__setitem__', '__delitem__'):
        vars()[method] = proxy(method)
    
    for method in ('clear', 'get', 'items', 'iteritems', 'iterkeys',
                   'itervalues', 'keys', 'pop', 'popitem', 'ritems',
                   'riteritems', 'riterkeys', 'ritervalues', 'rkeys', 'rvalues',
                   'setdefault', 'sort', 'update', 'values'):
        vars()['_' + method] = proxy(method)
    
    _dict = proxy('as_dict')
    
    del method, proxy
    
    #
    ### </meta>


class BoundRenderer(Renderer):
    
    def __init__(self, action, backends=None):
        super(BoundRenderer, self).__init__(backends=backends)
        self._action = action
    
    def __repr__(self):
        return "<BoundRenderer on %r>" % (self._action,)
    
    def __getattr__(self, shortcode):
        
        """
        Support use of decorator syntax to define new renderer backends.
        
        In this case, decorated functions should be methods which operate on a
        resource, and take no other arguments.
        
            >>> action = object()
            >>> r = BoundRenderer(action)
            >>> old_action_id = id(action)
            
            >>> @r.html
            ... def action(resource):
            ...     return "<html>...</html>"
            
            >>> id(action) == old_action_id # Object has not changed.
            True
        
        Functions will be wrapped internally, so that their function signature
        is that of a generic renderer backend. Accessing the 
        
            >>> resource = object()
            >>> r['html'](action, resource)
            '<html>...</html>'
        
        """
        
        if shortcode not in conneg.MIMETYPES:
            raise AttributeError(shortcode)
        
        def decorate(method):
            self[shortcode] = resource_method_wrapper(method)
            return self._action
        return decorate
    
    def __call__(self, resource):
        return super(BoundRenderer, self).__call__(self._action, resource)


def resource_method_wrapper(method):
    
    """
    Wrap a 0-ary resource method as a generic renderer backend.
    
        >>> @resource_method_wrapper
        ... def func(resource):
        ...     print repr(resource)
        
        >>> action = "abc"
        >>> resource = "def"
        
        >>> func(action, resource)
        'def'
    
    """
    
    def generic_renderer_backend(action, resource):
        return method(resource)
    return generic_renderer_backend


def not_acceptable(action, resource):
    """Respond, indicating that no acceptable entity could be generated."""
    
    from django.http import HttpResponse
    
    response = HttpResponse(status=406)  # Not Acceptable
    del response['Content-Type']
    return response
