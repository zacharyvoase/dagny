<!-- title: Tutorial -->

# The Dagny Tutorial

In this tutorial, I’m going to walk through creating a project with
authentication. The finished project will have signup, user pages, account
settings management, login and logout. It should provide a good grounding in how
to create resourceful web applications using Dagny.


## Setup

Begin by installing Dagny:

    :::bash
    pip install dagny  # or
    easy_install dagny

If you aren’t using pip yet, [you should be][pip].

  [pip]: http://python-distribute.org/pip_distribute.png

Now create a fresh Django project:

    ::bash
    django-admin.py startproject tutorial
    cd tutorial/
    chmod +x manage.py  # So we can run ./manage.py <command>
    mkdir templates/  # Project-wide templates will go here.

You need to edit the `settings.py` file; I’ve provided a sample file
[here](http://gist.github.com/444455), which you can drop into your project—just
fill in the two missing values (`ADMINS` and `SECRET_KEY`).

Set up the database and run a quick test:

    :::bash
    ./manage.py syncdb
    ./manage.py test

You should see a few lines of output, ending in the following:

    :::text
    ----------------------------------------------------------------------
    Ran 154 tests in 2.852s

    OK
    Destroying test database 'default'...

That means everything worked.


## The first resource: Users

Create an app called `users`:

    :::bash
    ./manage.py startapp users

This app will manage user and user session resources—this encompasses listing,
displaying, creating and editing users, and logging in and out. You’ll see,
however, that what would normally take a lot of code and configuration is
actually very simple to do with Dagny.

Create and start editing a `users.resources` module:

    :::bash
    vim users/resources.py

Add this basic structure:

    #!python
    from dagny import Resource, action

    class User(Resource):
        @action
        def index(self):
            pass

        @action
        def new(self):
            pass

        @action
        def create(self):
            pass

        @action
        def show(self, user_id):
            pass

        @action
        def edit(self, user_id):
            pass

        @action
        def update(self, user_id):
            pass

        @action
        def destroy(self, user_id):
            pass

As you can see, we’ve stubbed out 7 methods on the `User` resource: `index`,
`new`, `create`, `show`, `edit`, `update` and `destroy`. The expected behavior
of each of these is described in depth in the [URI reference](/uris).

<!-- TODO: finish -->
