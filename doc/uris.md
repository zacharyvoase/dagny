# URIs

This document describes in depth Dagny’s default URI scheme for resources. In
this aspect, Dagny follows the Rails convention, since it is well-established
and familiar to many developers.

You can also skip to the [URLconf reference](#urlconf).


## Actions

This is the default resource URL scheme. Dagny also supports configurable
[URL styles](#alternative_url_styles), but you should get familiar with the
defaults before moving on to those.


### Collections

The paths and their interaction with the standard HTTP methods are as follows:

Method   | Path             | Action         | Behavior
-------- | ---------------- | -------------- | -------------------------
`GET`    | `/users/`        | `User.index`   | List all users
`GET`    | `/users/new/`    | `User.new`     | Display new user form
`POST`   | `/users/`        | `User.create`  | Create new user
`GET`    | `/users/1/`      | `User.show`    | Display user 1
`GET`    | `/users/1/edit/` | `User.edit`    | Display edit user 1 form
`PUT`    | `/users/1/`      | `User.update`  | Update user 1
`DELETE` | `/users/1/`      | `User.destroy` | Delete user 1

Note that not all of these actions are required; for example, you may not wish
to provide `/users/new` and `/users/1/edit`, instead preferring to display the
relevant forms under `/users/` and `/users/1/`.

To work around the fact that `PUT` and `DELETE` are not typically supported in
browsers, you can add a `_method` parameter to a `POST` form to override the
request method:

    :::html+django
    <form method="post" action="/users/1/">
      <input type="hidden" name="_method" value="delete" />
      ...
    </form>


### Singular Resources

Method   | Path             | Action            | Behavior
-------- | ---------------- | ----------------- | --------------------------
`GET`    | `/account/`      | `Account.show`    | Display the account
`GET`    | `/account/new/`  | `Account.new`     | Display new account form
`POST`   | `/account/`      | `Account.create`  | Create the new account
`GET`    | `/account/edit/` | `Account.edit`    | Display edit account form
`PUT`    | `/account/`      | `Account.update`  | Update the account
`DELETE` | `/account/`      | `Account.destroy` | Delete the account

The same point applies here: you don’t need to specify all of these actions
every time.


## URLconf

### Collections

Pointing to a collection resource from your URLconf is relatively simple:

    #!python
    from dagny.urls import resources  # plural!
    from django.conf.urls.defaults import *

    urlpatterns = patterns('',
        (r'^users/', resources('myapp.resources.User'))
    )

You can customize this; for example, to use a slug/username instead of a numeric
ID:

    :::python
    urlpatterns = patterns('',
        (r'^users/', resources('myapp.resources.User', id=r'[\w\-_]+')),
    )

You can also restrict the actions that are routed to. Pass the `actions` keyword
argument to specify which of these you would like to be available:

    :::python
    urlpatterns = patterns('',
        (r'^users/', resources('myapp.resources.User',
            actions=('index', 'show', 'create', 'update', 'destroy'))),
    )

This is useful if you’re going to display the `new` and `edit` forms on the
`index` and `show` pages, for example. It may also prevent naming clashes if
you’re using slug identifiers in URIs.


### Singular Resources

For this, use the `resource()` helper:

    #!python
    from dagny.urls import resource  # singular!
    from django.conf.urls.defaults import *

    urlpatterns = patterns('',
        (r'^account/', resource('myapp.resources.User'))
    )

`resource()` is similar to `resources()`, but it only generates `show`, `new`
and `edit`, and doesn’t take an `id` parameter of any sort.


### Reversing URLs

`resource()` and `resources()` both attach names to the patterns they generate.
This allows you to use the `{% url %}` templatetag, for example:

    :::html+django
    <!-- A user creation (signup) form -->
    <form method="post" action="{% url myapp.resources.User#create %}">
      ...
    </form>

    <!-- Signup link -->
    <a href="{% url myapp.resources.User#new %}">Sign Up!</a>

    <!-- User profile link -->
    <a href="{% url myapp.resources.User#show user.id %}">View user</a>

    <!-- User editing link -->
    <a href="{% url myapp.resources.User#edit user.id %}">Edit user</a>

    <!-- User editing form -->
    <form method="post" action="{% url myapp.resources.User#update user.id %}">
      ...
    </form>

You can also use these references in `get_absolute_url()` methods that have been
wrapped with `@models.permalink`:

    :::python
    from django.db import models

    class User(models.Model):
        # ... snip! ...

        @models.permalink
        def get_absolute_url(self):
            return ("myapp.resources.User#show", self.id)

Of course, having to write out the full path to the resource is quite
cumbersome, so you can give a `name` keyword argument to either of the URL
helpers, and use the shortcut:

    :::python
    # In urls.py:
    urlpatterns = patterns('',
        (r'^users/', resources('myapp.resources.User', name='User'))
    )

    # In models.py:
    class User(models.Model):
        @models.permalink
        def get_absolute_url(self):
            return ("User#show", self.id)

    # In resources.py:
    class User(Resource):
        # ... snip! ...
        @action
        def update(self, user_id):
            # ... validate the form and save the user ...
            return redirect("User#show", self.user.id)

These shortcuts are also available in the templates:

    :::html+django
    <form method="post" action="{% url User#create %}">
      ...
    </form>

    <a href="{% url User#new %}">Sign Up!</a>

    <a href="{% url User#show user.id %}">View user</a>

    <a href="{% url User#edit user.id %}">Edit user</a>

    <form method="post" action="{% url User#update user.id %}">
      ...
    </form>


## Alternative URL Styles

Dagny supports configurable *URL styles*, of which the default is only a single
instance. Following are the other two which Dagny comes packaged with.

To use an alternative style, create a `dagny.urls.router.URLRouter` with the
style and use the `resources()` and `resource()` methods defined on that as
your URLconf helpers.

    :::python
    from dagny.urls.router import URLRouter
    from myapp import MyURLStyle

    style = MyURLStyle()
    router = URLRouter(style)

    # Use these instead when defining your URLs.
    resources, resource = router.resources, router.resource

The built-in alternative styles already have stub modules with the two helpers
defined.


### AtomPub URLs

This style matches the URL conventions used in the
[Atom Publishing Protocol][app].

  [app]: http://tools.ietf.org/html/rfc5023

Usage: `from dagny.urls.atompub import *`

Path               | Action(s)
------------------ | ----------------------------------------------
`/accounts/`       | `Account.index`, `Account.create`
`/accounts/new`    | `Account.new`
`/accounts/1`      | `Account.show`, `Account.update`, `Account.destroy`
`/accounts/1/edit` | `Account.edit`


### Rails URLs

These URLs mimic those of Rails, including the optional format extensions.

Usage: `from dagny.urls.rails import *`

Path               | Action(s)
------------------ | ----------------------------------------------
`/accounts`        | `Account.index`, `Account.create`
`/accounts.json`   | 〃 (with kwargs `{'format': 'json'}`)
`/accounts/`       | 〃
`/accounts/new`    | `Account.new`
`/accounts/1`      | `Account.show`, `Account.update`, `Account.destroy`
`/accounts/1/`     | 〃
`/accounts/1.json` | 〃 (with kwargs `{'format': 'json'}`)
`/accounts/1/edit` | `Account.edit`

**Note**: due to limitations of the URLconf system—to wit, the inability to mix
keyword and positional arguments in the same URL—your IDs/slugs have to come
in as named parameters. By default, the parameter will be called `id`, but you
can select a different one using the `id` keyword argument to the URL helpers:

    :::python
    urlpatterns = patterns('',
        # To get the slug, use `self.params['slug']` on the `Post` resource.
        # Also note: there is no terminating slash on the top-level regex.
        (r'posts', resources('myapp.resources.Post', name='Post',
                             id=('slug', r'[\w\-]+'))),
    )

Another caveat: do not terminate your top-level regex with a slash, or the
format extension on the resource index (e.g. `/posts.json`) won't work.
