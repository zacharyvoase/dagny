# -*- coding: utf-8 -*-

from dagny.renderer import Renderer
from dagny.resource import Resource
from dagny.utils import resource_name


class Action(object):
    
    """
    A descriptor for wrapping an action method.
    
        >>> action = Action
        >>> class X(Resource):
        ...     @action
        ...     def show(self):
        ...         self.attr1 = 'a'
    
    Appears as an `Action` on the class (and other objects):
    
        >>> X.show  # doctest: +ELLIPSIS
        <Action '#show' at 0x...>
        >>> X.show.render  # doctest: +ELLIPSIS
        <dagny.renderer.Renderer object at 0x...>
    
    Appears as a `BoundAction` on an instance:
    
        >>> x = X._new(object())
        >>> x.show  # doctest: +ELLIPSIS
        <BoundAction 'X#show' at 0x...>
        >>> x.show.render  # doctest: +ELLIPSIS
        <bound method BoundAction.render of <BoundAction 'X#show' at 0x...>>
    
    """
    
    def __init__(self, method):
        self.method = method
        self.name = method.__name__
        self.render = Renderer(self)
    
    def __repr__(self):
        return "<Action '#%s' at 0x%x>" % (self.name, id(self))
    
    def __get__(self, resource, resource_cls):
        if isinstance(resource, Resource):
            return BoundAction(self, resource, resource_cls)
        return self


class BoundAction(object):
    
    """An action which has been bound to a specific resource instance."""
    
    def __init__(self, action, resource, resource_cls):
        self.action = action
        self.resource = resource
        self.resource_cls = resource_cls
        self.resource_name = resource_name(resource_cls)
    
    def __repr__(self):
        return "<BoundAction '%s#%s' at 0x%x>" % (self.resource_name, self.action.name, id(self))
    
    def __call__(self, format=None):
        response = self.action.method(self.resource, *self.resource.args)
        if response:
            return response
        return self.render()
    
    def render(self):
        return self.action.render(self.resource)
