# -*- coding: utf-8 -*-

from dagny.renderer import Renderer
from dagny.utils import camel_to_underscore, resource_name

from django.shortcuts import render_to_response
from django.template import RequestContext


@Renderer.generic('html')
def render_html(action, resource):
    resource_label = camel_to_underscore(resource_name(resource))
    template_path_prefix = getattr(resource, 'template_path_prefix', "")
    template_name = "%s%s/%s.html" % (template_path_prefix, resource_label, action.name)
    
    return render_to_response(template_name, {
        'self': resource
    }, context_instance=RequestContext(resource.request))
