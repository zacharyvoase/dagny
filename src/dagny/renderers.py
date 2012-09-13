"""Generic, built-in renderers."""

from dagny.action import Action
from dagny.utils import camel_to_underscore, resource_name


@Action.RENDERER.html
def render_html(action, resource, content_type=None, status=None,
                current_app=None):

    """
    Render an appropriate HTML response for an action.

    This is a generic renderer backend which produces HTML responses. It uses
    the name of the resource and current action to generate a template name,
    then renders the template with a `RequestContext`.

    To retrieve the template name, the resource name is first turned from
    CamelCase to lowercase_underscore_separated; if the class name ends in
    `Resource`, this is first removed from the end. For example:

        User => user
        UserResource => user
        NameXYZ => name_xyz
        XYZName => xyz_name

    You can optionally define a template path prefix on your `Resource` like
    so:

        class User(Resource):
            template_path_prefix = 'auth/'
            # ...

    The template name is assembled from the template path prefix, the
    re-formatted resource name, and the current action name. So, for a `User`
    resource, with `template_path_prefix = 'auth/'`, and an action of `show`,
    the template name would be:

        auth/user/show.html

    Finally, this is rendered using `django.shortcuts.render()`. The resource
    is passed into the context as `self`, so that attribute assignments from
    the action will be available in the template. This also uses
    `RequestContext`, so configured context processors will also be available.
    """

    from django.shortcuts import render

    resource_label = camel_to_underscore(resource_name(resource))
    template_path_prefix = getattr(resource, 'template_path_prefix', "")
    template_name = "%s%s/%s.html" % (template_path_prefix, resource_label,
                                      action.name)

    return render(resource.request, template_name, {'self': resource},
                  content_type=content_type, status=status,
                  current_app=current_app)
