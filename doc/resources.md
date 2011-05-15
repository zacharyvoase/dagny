# Resources

The **resource** is the most basic concept in writing RESTful applications. A
resource is identified by a URI, and clients interact with resources
using the standard HTTP methods. Detailed information on the URI schema and the
behavior of resources over HTTP is provided in the [URI documentation](/uris).


## Defining Resources

Resources are subclasses of `dagny.Resource`. Actions are methods on these
subclasses, decorated with `@action`. Here’s a short example:

    #!python
    from dagny import Resource, action
    from django.shortcuts import get_object_or_404, redirect

    from django.contrib.auth import forms, models

    class User(Resource):

        @action
        def index(self):
            self.users = models.User.objects.all()

        @action
        def new(self):
            self.form = forms.UserCreationForm()

        @action
        def create(self):
            self.form = forms.UserCreationForm(request.POST)
            if self.form.is_valid():
                self.user = self.form.save()
                return redirect(self.user)

            response = self.new.render()
            response.status_code = 403 # Forbidden
            return response

        @action
        def show(self, username):
            self.user = get_object_or_404(models.User, username=username)

        @action
        def edit(self, username):
            self.user = get_object_or_404(models.User, username=username)
            self.form = forms.UserChangeForm(instance=self.user)

        @action
        def update(self, username):
            self.user = get_object_or_404(models.User, username=username)
            self.form = forms.UserChangeForm(self.request.POST, instance=self.user)
            if self.form.is_valid():
                self.form.save()
                return redirect(self.user)

            response = self.edit.render()
            response.status_code = 403
            return response

        @action
        def destroy(self, username):
            self.user = get_object_or_404(models.User, username=username)
            self.user.delete()
            return redirect('/users')

`Resource` uses [django-clsview][] to define class-based views; the extensive
use of `self` is safe because a new instance is created for each request.

  [django-clsview]: http://github.com/zacharyvoase/django-clsview

You might notice that there are no explicit calls to `render_to_response()`;
most of the time you’ll want to render the same templates: `"user/index.html"`,
`"user/new.html"`, `"user/show.html"` and `"user/edit.html"`. Therefore, if your
action doesn’t return anything (i.e. returns `None`), a template corresponding
to the resource and action will be rendered. See the
[renderer documentation](/renderer) for more information.


### Decorating Resources

If you want to apply a view decorator to an entire `Resource`, you can use the
`_decorate()` method (as provided by `django-clsview`):

    :::python
    class User(Resource):
        ...
    User = User._decorate(auth_required)

Note that this returns a *new resource*, so you need to re-assign the result to
the old name.


### Decorating Actions

Because actions don’t have the typical function signature of a Django view (i.e.
`view(request, *args, **kwargs)`), most view decorators won’t work on an action
method. For this reason, Dagny provides a simple decorator-wrapper which will
adapt a normal view decorator to work on an action method. Use it like this:

    :::python
    class User(Resource):
        @action
        @action.deco(auth_required)
        def edit(self, username):
            ...

`deco()` is a staticmethod on the `Action` class, purely for convenience.
Remember: `@action.deco()` must come *below* `@action`, otherwise you’re likely
to get a cryptic error message at runtime.
