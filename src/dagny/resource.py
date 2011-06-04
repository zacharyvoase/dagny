# -*- coding: utf-8 -*-

from django.http import Http404, HttpResponseNotAllowed
from djclsview import View

__all__ = ['Resource']


class Resource(View):

    def __init__(self, request, *args, **params):
        self.request = request
        self.args = args
        self.params = params
        self._called_yet = False

    def __call__(self):
        """Dispatch to an action based on HTTP method + URL."""

        # The problem with defining a resource as a callable is that a
        # reference to `self` from a Django template (in v1.3) will attempt to
        # call the resource again.
        if self._called_yet:
            return self
        self._called_yet = True

        method = self.request.POST.get('_method', self.request.method).upper()
        try:
            method_action_map = self.params.pop('methods')
        except KeyError:
            raise ValueError("Expected 'methods' dict in view kwargs")
        return self._route(method, method_action_map)()

    def _route(self, method, method_action_map):

        """
        Resolve an HTTP method and an HTTP method -> action mapping to a view.

        There are two sources for the list of 'defined methods' on a given URL:
        the HTTP method -> action map passed in to this method, and the actions
        which are defined on this `Resource` class. If the intersection of
        these two lists is empty--to wit, no methods are defined for the
        current URL--return a stub 404 view. Otherwise, if an HTTP method is
        sent which is not in *both* these lists, return a 405 'Not Allowed'
        view (which will contain the list of accepted methods at this URL).

        If the HTTP method sent is in the method -> action map, and the mapped
        action is defined on this `Resource`, return that action (which will be
        a callable `BoundAction` instance).
        """

        allowed_methods = self._allowed_methods(method_action_map)
        if method not in allowed_methods:
            # If *no* methods are defined for this URL, return a 404.
            if not allowed_methods:
                return not_found
            return lambda: HttpResponseNotAllowed(allowed_methods)

        action_name = method_action_map[method]
        return getattr(self, action_name)

    def _allowed_methods(self, method_action_map):
        allowed_methods = []
        for meth, action_name in method_action_map.items():
            if hasattr(self, action_name):
                allowed_methods.append(meth)
        return allowed_methods

    def _format(self):
        """Return a mimetype shortcode, in case there's no Accept header."""

        if self.params.get('format'):
            return self.params['format'].lstrip('.')
        return self.request.GET.get('format')


def not_found():
    """Stub function to raise `django.http.Http404`."""

    raise Http404
