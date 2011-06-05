from django.conf.urls import defaults


class URLRouter(object):

    """
    Responsible for generating include()-able URLconfs for resources.

    Accepts only one argument on instantiation, `style`. This should be a
    callable which accepts an action parameter, a routing mode and an ID regex,
    and returns a regular expression with a route for that action. You should
    only need to use the styles already defined in `dagny.urls.styles`.
    """

    def __init__(self, style):
        self.style = style

    def _make_patterns(self, resource_name, id, name, actions, urls):

        """
        Construct an `include()` with all the URLs for a resource.

        :param resource_name:
            The full path to the resource (e.g.  `myapp.resources.User`).
        :param id:
            The ID parameter, either as a regex fragment or a `(name, regex)`
            pair, which will normally be translated by the URL style to a named
            group in the URL.
        :param name:
            The name for this resource, which will be used to generate named
            URL patterns (e.g. if name is 'User', URLs will be 'User#index',
            'User#show' etc.). If `None`, defaults to `resource_name`.
        :param actions:
            The actions to generate (named) routes for. If `None`, a route and
            a name will be generated for every one defined by the chosen URL
            style.
        :param urls:
            A list of the URLs to define patterns for. Must be made up only of
            'member', 'collection', 'new', 'edit', 'singleton' and
            'singleton_edit'.
        """

        if actions is not None:
            actions = set(actions)
        if name is None:
            name = resource_name

        urlpatterns = []
        for url in urls:
            # URLStyle.__call__(url_name, id_pattern)
            #     => (url_pattern, {method: action, ...})
            pattern, methods = self.style(url, id)
            # Filter methods dict to only contain the selected actions.
            methods = dict(
                (method, action) for method, action in methods.iteritems()
                if (actions is None) or (action in actions))
            # Add named url patterns, one per action. Note that we will have
            # duplicate URLs in some cases, but this is so that
            # `{% url User#show %}` can be distinguished from
            # `{% url User#update %}` when it makes sense.
            for action in methods.itervalues():
                urlpatterns.append(defaults.url(pattern, resource_name,
                                                kwargs={'methods': methods},
                                                name=("%s#%s" % (name, action))))
        return defaults.include(defaults.patterns('', *urlpatterns))

    def resources(self, resource_name, id=r'\d+', actions=None, name=None):
        return self._make_patterns(resource_name, id, name, actions,
                                   ['collection', 'new', 'member', 'edit'])

    def resource(self, resource_name, actions=None, name=None):
        return self._make_patterns(resource_name, '', name, actions,
                                   ['singleton', 'new', 'singleton_edit'])
