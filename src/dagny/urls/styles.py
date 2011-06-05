class URLStyle(object):

    """
    Generic class for defining resource URL styles.

    `URLStyle` can be used to create callables which will work for the
    interface defined in `dagny.urls.router.URLRouter`. Subclass and override
    the `collection()`, `new()`, `member()`, `edit()`, `singleton()` and
    `singleton_edit()` methods to customize your URLs. You can use one of the
    several defined styles in this module as a template.
    """

    METHODS = {
        'collection': {
            'GET': 'index',
            'POST': 'create'
        },
        'member': {
            'GET': 'show',
            'POST': 'update',
            'PUT': 'update',
            'DELETE': 'destroy'
        },
        'new': {'GET': 'new'},
        'edit': {'GET': 'edit'},
        'singleton': {
            'GET': 'show',
            'POST': 'update',
            'PUT': 'update',
            'DELETE': 'destroy'
        },
        'singleton_edit': {'GET': 'edit'},
    }

    def __call__(self, url, id_param):
        id_regex = self._get_id_regex(id_param)

        if url in ('member', 'edit'):
            return getattr(self, url)(id_regex), self.METHODS[url]
        return getattr(self, url)(), self.METHODS[url]

    def _get_id_regex(self, id_param):

        """
        Resolve `(name, regex)` => `'?P<name>regex'`.

        Since the style methods should add parentheses around the ID regex
        fragment, the output for named ID parameters is not surrounded by
        parentheses itself.
        """

        if isinstance(id_param, basestring):
            return id_param
        elif isinstance(id_param, tuple):
            if len(id_param) != 2:
                raise ValueError("id param must be a (name, regex) pair")
            name, regex = id_param
            return '?P<%s>%s' % (name, regex)
        raise TypeError('id param must be a string or (name, regex) pair, '
                        'not %r' % (type(id_param),))

    # Publicly-overrideable methods for customizing style behaviour.

    def collection(self):
        raise NotImplementedError

    def new(self):
        raise NotImplementedError

    def member(self, id_regex):
        raise NotImplementedError

    def edit(self, id_regex):
        raise NotImplementedError

    def singleton(self):
        raise NotImplementedError

    def singleton_edit(self):
        raise NotImplementedError


class DjangoURLStyle(URLStyle):

    """
    Standard Django-style URLs.

       URL            | action | args   | kwargs
       ---------------+--------+--------+--------
       /posts/        | index  | ()     | {}
       /posts/new/    | new    | ()     | {}
       /posts/1/      | show   | ('1',) | {}
       /posts/1/edit/ | edit   | ('1',) | {}
    """

    def collection(self):
        return r'^$'

    def new(self):
        return r'^new/$'

    def member(self, id_regex):
        return r'^(%s)/$' % (id_regex,)

    def edit(self, id_regex):
        return r'^(%s)/edit/$' % (id_regex,)

    def singleton(self):
        return r'^$'

    def singleton_edit(self):
        return r'^edit/$'


class AtomPubURLStyle(URLStyle):

    """
    Atom Publishing Protocol-style URLs.

    The main difference between this and Django-style URLs is the lack of
    trailing slashes on leaf nodes.

        URL           | action | args   | kwargs
        --------------+--------+--------+--------
        /posts/       | index  | ()     | {}
        /posts/new    | new    | ()     | {}
        /posts/1      | show   | ('1',) | {}
        /posts/1/edit | edit   | ('1',) | {}
    """

    def collection(self):
        return r'^$'

    def new(self):
        return r'^new$'

    def member(self, id_regex):
        return r'^(%s)$' % (id_regex,)

    def edit(self, id_regex):
        return r'^(%s)/edit$' % (id_regex,)

    def singleton(self):
        return r'^$'

    def singleton_edit(self):
        return r'^edit$'


class RailsURLStyle(URLStyle):

    r"""
    Ruby on Rails-style URLs.

    This URL style is quite advanced; it will also capture format extensions
    and pass them through as a kwarg. As with `AtomPubURLStyle`, trailing
    slashes are not mandatory on leaf nodes.

        URL           | action | args | kwargs
        --------------+--------+------+------------------------------
        /posts        | index  | ()   | {}
        /posts.json   | index  | ()   | {'format': 'json'}
        /posts/       | index  | ()   | {}
        /posts/new    | new    | ()   | {}
        /posts/1      | show   | ()   | {'id': '1'}
        /posts/1.json | show   | ()   | {'id': '1', 'format': 'json'}
        /posts/1/     | show   | ()   | {'id': '1'}
        /posts/1/edit | edit   | ()   | {'id': '1'}

    **Note**: due to limitations of the URLconf system, your IDs/slugs have to
    come in as named parameters. By default, the parameter will be called `id`,
    but you can select a different one using the `id` keyword argument to the
    URL helpers:

        urlpatterns = patterns('',
            (r'posts', resources('myapp.resources.Post', name='Post',
                                 id=('slug', r'[\w\-]+'))),
        )

    Another caveat: do not terminate your inclusion regex with a slash, or the
    format extension on the resource index won't work.

    You can customize the format extension regex (and hence the kwarg name) by
    subclassing and overriding the `FORMAT_EXTENSION_RE` attribute, e.g.:

        class MyRailsURLStyle(RailsURLStyle):
            FORMAT_EXTENSION_RE = r'(?P<accept>[A-Za-z0-9]+)'
    """

    FORMAT_EXTENSION_RE = r'(?P<format>\.\w[\w\-\.]*)'

    def _get_id_regex(self, id_param):
        """Co-erce *all* IDs to named parameters, defaulting to `'id'`."""

        if isinstance(id_param, basestring) and not id_param.startswith('?P<'):
            return super(RailsURLStyle, self)._get_id_regex(('id', id_param))
        return super(RailsURLStyle, self)._get_id_regex(id_param)

    def collection(self):
        return r'^%s?/?$' % (self.FORMAT_EXTENSION_RE,)

    def new(self):
        return r'^/new/?$'

    def member(self, id_regex):
        return r'^/(%s)%s?/?$' % (id_regex, self.FORMAT_EXTENSION_RE)

    def edit(self, id_regex):
        return r'^/(%s)/edit/?$' % (id_regex,)

    def singleton(self):
        return r'^%s?/?$' % (self.FORMAT_EXTENSION_RE,)

    def singleton_edit(self):
        return r'^/edit/?$'
