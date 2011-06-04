# URIs

This document describes in depth Dagny’s default URI scheme for resources. In
this aspect, Dagny follows the Rails convention, since it is well-established
and familiar to many developers.

You can also skip to the [URLconf reference](#urlconf).


## Types of Resource

Dagny supports two types of resource: collections and singular resources.
Collections are lists of uniquely-identifiable members, such as blog posts,
users and products. Singular resources (a.k.a. singletons) are resources of
which only one ever exists, and are typically tied to the currently logged-in
user (e.g. the current user's profile, the user session, etc.).


## The Default URL Scheme

What follows is the default URL scheme for resources. Dagny also supports
configurable [URL styles](#alternative_url_styles), but you should get familiar
with the defaults before moving on to those.


### Collections

The paths and their interaction with the standard HTTP methods are as follows:

Name       | Path             | Method   | Action    | Behavior
---------- | ---------------- | -------- | --------- | --------------------------------
Collection | `/users/`        | `GET`    | `index`   | List all users
           |                  | `POST`   | `create`  | Create a user
Member     | `/users/1/`      | `GET`    | `show`    | Display user 1
           |                  | `PUT`    | `update`  | Edit user 1
           |                  | `POST`   | `update`  | Edit user 1
           |                  | `DELETE` | `destroy` | Delete user 1
New        | `/users/new/`    | `GET`    | `new`     | Display the new user form
Edit       | `/users/1/edit/` | `GET`    | `edit`    | Display the edit form for user 1

Note that not all of these actions are required; for example, you may not wish
to provide `/users/new` and `/users/1/edit`, instead preferring to display the
relevant forms under `/users/` and `/users/1/`. You may also support only
certain HTTP methods at a given path; for example, only allowing `GET` on
`/users/1/`.

To work around the fact that `PUT` and `DELETE` are not typically supported in
browsers, you can add a `_method` parameter to a `POST` form to override the
request method:

    :::html+django
    <form method="post" action="/users/1/">
      <input type="hidden" name="_method" value="delete" />
      ...
    </form>


### Singular Resources

Name   | Path             | Method   | Action            | Behavior
------ | ---------------- | -------- | ----------------- | -----------------------------
Member | `/account/`      | `GET`    | `Account.show`    | Display the account
       |                  | `POST`   | `Account.create`  | Create the new account
       |                  | `PUT`    | `Account.update`  | Update the account
       |                  | `DELETE` | `Account.destroy` | Delete the account
New    | `/account/new/`  | `GET`    | `Account.new`     | Display the new account form
Edit   | `/account/edit/` | `GET`    | `Account.edit`    | Display the edit account form

The same point applies here: you don’t need to specify all of these actions
every time.


## The URLconf

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
        (r'^users/', resources('myapp.resources.User',
                               id=r'[\w\-_]+')),
    )

If you'd like the ID to appear as a named group in the regex (and hence be
passed to your resource in `self.params` instead of as a positional argument),
pass it as a two-tuple of `(param_name, regex)`:

    :::python
    urlpatterns = patterns('',
        (r'^users/', resources('myapp.resources.User',
                               id=('username', r'[\w\-_]+'))),
    )

This is especially useful if your URL already captures a parameter, as Django
does not support mixing positional and keyword arguments in a URL.

You can also restrict the actions that are routed to. Pass the `actions` keyword
argument to specify which of these you would like to be available:

    :::python
    urlpatterns = patterns('',
        (r'^users/', resources('myapp.resources.User',
            actions=('index', 'show', 'create', 'update', 'destroy'))),
    )

This is useful if you’re going to display the `new` and `edit` forms on the
`index` and `show` pages, for example. Excluding `new` and `edit` may also
prevent naming clashes if you’re using slug identifiers in URIs.

**N.B.:** most of the time, you won't need to use the `actions` keyword
argument; if you just leave actions undefined, Dagny will automatically return
the appropriate responses. The only case where `actions` would be useful is if
those actions *are* defined on the resource but you don't want routes to them
to be created.


### Singular Resources

For this, use the `resource()` helper:

    #!python
    from dagny.urls import resource  # singular!
    from django.conf.urls.defaults import *

    urlpatterns = patterns('',
        (r'^account/', resource('myapp.resources.User'))
    )

`resource()` is similar to `resources()`, but it only generates `show`, `new`
and `edit`, and doesn’t take an `id` parameter.


## Reversing URLs

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
