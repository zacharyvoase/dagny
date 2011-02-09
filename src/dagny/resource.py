# -*- coding: utf-8 -*-

from django.http import Http404, HttpResponseNotAllowed
from djclsview import View

__all__ = ['Resource']


METHOD_ACTION_MAP = {
    'singular': {
        'show': {
            'GET': 'show',
            'POST': 'create',
            'PUT': 'update',
            'DELETE': 'destroy',
        },
        'new': {'GET': 'new'},
        'edit': {'GET': 'edit'},
    },

    'plural': {
        'index': {
            'GET': 'index',
            'POST': 'create'
        },
        'show': {
            'GET': 'show',
            'PUT': 'update',
            'POST': 'update',
            'DELETE': 'destroy',
        },
        'new': {'GET': 'new'},
        'edit': {'GET': 'edit'},
    }
}


class Resource(View):

    def __init__(self, request, *args, **params):
        self.request = request
        self.args = args
        self.params = params

    def __call__(self):
        """Dispatch to an action based on HTTP method + URL."""

        method = self.request.POST.get('_method', self.request.method).upper()
        url_action = self.params.pop('action')
        mode = self.params.pop('mode', None)
        return self._route(method, url_action, mode=mode)()

    def _route(self, method, url_action, mode=None):

        """
        Resolve a method, URL action and (optionally) mode to a 0-ary callable.

        The default behaviour is to map the URL action and the method via the
        `METHOD_ACTION_MAP` to an action on this resource.
        """

        try:
            action_name = METHOD_ACTION_MAP[mode][url_action][method]
        except KeyError:
            # Assume the developer knows what he/she is doing.
            action_name = url_action

        if hasattr(self, action_name):
            return getattr(self, action_name)
        elif mode:
            return lambda: self._not_allowed(mode, url_action)
        else:
            return self._not_found

    def _not_allowed(self, mode, url_action):
        """Return a `HttpResponseNotAllowed` for this mode and URL action."""

        allowed_methods = []
        for meth, action_name in METHOD_ACTION_MAP[mode][get_action].items():
            if hasattr(self, action_name):
                allowed_methods.append(meth)
        return HttpResponseNotAllowed(allowed_methods)

    def _not_found(self):
        raise Http404

    def _format(self):
        """Return a mimetype shortcode, in case there's no Accept header."""

        return self.request.GET.get('format')
