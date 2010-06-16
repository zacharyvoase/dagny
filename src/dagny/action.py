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
        <BoundRenderer on <Action '#show' at 0x...>>
    
    Appears as a `BoundAction` on an instance:
    
        >>> x = X._new(object())
        >>> x.show  # doctest: +ELLIPSIS
        <BoundAction 'X#show' at 0x...>
        >>> x.show.render  # doctest: +ELLIPSIS
        <bound method BoundAction.render of <BoundAction 'X#show' at 0x...>>
    
    ## Actions and Rendering
    
    The API for `Action` instances has been fine-tuned to allow an easy
    interface with the renderer system. When accessed from inside the class
    definition, `show.render` is a `BoundRenderer` instance, so you're just
    using the standard decorator syntax for defining new renderer backends:
    
        class User(Resource):
            
            @action
            def show(self, username):
                self.user = get_object_or_404(User, username=username)
            
            @show.render.json
            def show(self):
                return JSONResponse(self.user.as_dict())
            
            # You can also un-define renderer backends for a single action:
            del show.render['html']
            
            # Or assign generic backends for a particular action:
            show.render['html'] = my_generic_html_backend
    
    When accessed via a resource *instance*, `show.render` will be the
    `render()` method of a `BoundAction`, and calling it will invoke the full
    rendering process for that particular action, on the current resource. This
    is very useful when handling forms; for example:
    
        class User(Resource):
            
            @action
            def edit(self, username):
                self.user = get_object_or_404(User, username=username)
                self.form = UserForm(instance=self.user)
                # Here the default HTML renderer will kick in; you should
                # display the edit user form in a "user/edit.html" template.
            
            @action
            def update(self, username):
                self.user = get_object_or_404(User, username=username)
                self.form = UserForm(instance=self.user)
                if self.form.is_valid():
                    self.form.save()
                    # Returns a response, action ends here.
                    return redirect(self.user)
                
                # Applies the `edit` renderer to *this* request, thus rendering
                # the "user/edit.html" template but with this resource (and
                # hence this `UserForm` instance, which contains errors).
                response = self.edit.render()
                response.status_code = 403  # Forbidden
                return response
    
    It makes sense to write the `user/edit.html` template so that it renders
    forms dynamically; this means the filled-in fields and error messages will
    propagate automatically, without any extra work on your part.
    """
    
    # Global renderer to allow definition of generic renderer backends.
    RENDERER = Renderer()
    
    def __init__(self, method):
        self.method = method
        self.name = method.__name__
        self.render = self.RENDERER._bind(self)
    
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
    
    def __call__(self):
        response = self.action.method(self.resource, *self.resource.args)
        if response:
            return response
        return self.render()
    
    def render(self):
        return self.action.render(self.resource)
