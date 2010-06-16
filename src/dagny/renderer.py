# -*- coding: utf-8 -*-

from dagny import conneg


class Renderer(object):
    
    GENERIC_RENDERERS = []
    
    @classmethod
    def generic(cls, shortcode):
        
        """
        Declare a function as a generic renderer for a given shortcode.
        
        Example:
        
            @Renderer.generic('html')
            def render_html(action, resource):
                resource_label = camel_to_underscore(resource_name(resource))
                template_path_prefix = getattr(resource, 'template_path_prefix', "")
                template_name = "%s%s/%s.html" % (template_path_prefix, resource_label, action.name)
                
                return render_to_response(template_name, {
                    'self': resource
                }, context_instance=RequestContext(resource.request))
        
        """
        
        def decorator(function):
            cls.GENERIC_RENDERERS.append((shortcode, function))
            return function
        return decorator
    
    def __init__(self, action):
        self._action = action
        self._renderers = self.GENERIC_RENDERERS[:]
    
    def __getattr__(self, shortcode):
        if shortcode not in conneg.MIMETYPES:
            raise AttributeError(shortcode)
        
        def decorate(method):
            self[shortcode] = resource_method_wrapper(method)
            return self._action
        return decorate
    
    def __getitem__(self, shortcode):
        for sc, render_func in reversed(self._renderers):
            if sc == shortcode:
                return render_func
        raise KeyError(shortcode)
    
    def __setitem__(self, shortcode, render_func):
        self._renderers.append((shortcode, render_func))
    
    def __delitem__(self, shortcode):
        for i, renderer in enumerate(self._renderers):
            if renderer[0] == shortcode:
                self._renderers[i] = None
        self._renderers = filter(None, self._renderers)
    
    def __call__(self, resource):
        shortcode = None
        accept_header = resource.request.META.get('HTTP_ACCEPT')
        if accept_header:
            shortcode = conneg.match_accept(accept_header, self._shortcodes())
        if shortcode is None:
            shortcode = resource._get_format()
        if shortcode is None:
            shortcode = 'html'
        
        return self[shortcode](self._action, resource)
    
    def _shortcodes(self):
        return [shortcode for shortcode, render_func in self._renderers]


def resource_method_wrapper(method):
    """Wrap a resource method as a generic renderer."""
    
    def generic_renderer(action_instance, resource_instance):
        return method(resource_instance)
    return generic_renderer
