from django.conf.urls.defaults import include, patterns, url


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

    def _make_patterns(self, resource_name, id, name,
                      actions, mode, action_patterns):

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
            The actions to generate routes for. If `None`, a route will be
            generated for every pair defined in `action_patterns`.
        :param mode:
            The value of the 'mode' kwarg to set in the URLs. This will also be
            passed into the URL style as the second parameter.
        :param action_patterns:
            A list of pairs containing the action name and the value of the
            'action' URL kwarg it should map to.
        """

        if actions is None:
            actions = set(action[0] for action in action_patterns)
        else:
            actions = set(actions)

        if name is None:
            name = resource_name

        urls = []
        for action_name, action_param in action_patterns:
            if action_name in actions:
                pattern = self.style(action_param, mode, id)
                urls.append(url(pattern, resource_name,
                                kwargs={'action': action_param, 'mode': mode},
                                name=("%s#%s" % (name, action_name))))
        return include(patterns('', *urls))

    def resources(self, resource_name, id=r'\d+', actions=None, name=None):
        return self._make_patterns(resource_name, id, name, actions, 'plural',
                                  [
                                      # (action_name, action_param)
                                      ('index',    'index'),
                                      ('create',   'index'),
                                      ('new',      'new'),
                                      ('show',     'show'),
                                      ('update',   'show'),
                                      ('destroy',  'show'),
                                      ('edit',     'edit'),
                                  ])

    def resource(self, resource_name, actions=None, name=None):
        return self._make_patterns(resource_name, '', name, actions, 'singular',
                                  [
                                      # (action_name, action_param)
                                      ('show',     'show'),
                                      ('create',   'show'),
                                      ('update',   'show'),
                                      ('destroy',  'show'),
                                      ('new',      'new'),
                                      ('edit',     'edit'),
                                  ])
