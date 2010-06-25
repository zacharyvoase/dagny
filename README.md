# Dagny

Dagny is a [Django][] adaptation of [Ruby on Rails][]’s Resource-Oriented
Architecture (a.k.a. ‘RESTful Rails’).  
Dagny makes it *really easy* to build **resourceful** web applications.

  [django]: http://djangoproject.com/
  [ruby on rails]: http://rubyonrails.org/

You can read the full documentation [here](http://zacharyvoase.github.com/dagny/).

At present, this project is in an experimental phase, so APIs are very liable to
change. **You have been warned.**

P.S.: the name is [a reference][dagny taggart].

  [dagny taggart]: http://en.wikipedia.org/wiki/List_of_characters_in_Atlas_Shrugged#Dagny_Taggart


## Motivation

Rails makes building RESTful web applications incredibly easy, because
resource-orientation is baked into the framework—it’s actually harder to make
your app *un*RESTful.

I wanted to build a similar system for Django; one that made it incredibly
simple to model my resources and serve them up with the minimum possible code.

One of the most important requirements was powerful yet simple content
negotiation: separating application logic from the rendering of responses makes
writing an API an effortless task.

Finally, as strong as Rails’s inspiration was, it still needed to be consistent
with the practices and idioms of the Django and Python ecosystems. Dagny doesn’t
use any metaclasses (yet), and the code is well-documented and readable by most
Pythonista’s standards.


## Appetizer

Define a resource:

    from dagny import Resource, action
    from django.shortcuts import get_object_or_404, redirect
    from polls import forms, models
    
    class Poll(Resource):
        
        @action
        def index(self):
            self.polls = models.Poll.objects.all()
        
        @action
        def new(self):
            self.form = forms.PollForm()
        
        @action
        def create(self):
            self.form = forms.PollForm(self.request.POST)
            if self.form.is_valid():
                self.poll = self.form.save()
                return redirect("Poll#show", self.poll.id)
            
            return self.new.render()
        
        @action
        def edit(self, poll_id):
            self.poll = get_object_or_404(models.Poll, id=int(poll_id))
            self.form = forms.PollForm(instance=self.poll)
        
        @action
        def update(self, poll_id):
            self.poll = get_object_or_404(models.Poll, id=int(poll_id))
            self.form = forms.PollForm(self.request.POST, instance=self.poll)
            if self.form.is_valid():
                self.form.save()
                return redirect("Poll#show", self.poll.id)
            
            return self.edit.render()
        
        @action
        def destroy(self, poll_id):
            self.poll = get_object_or_404(models.Poll, id=int(poll_id))
            self.poll.delete()
            return redirect("Poll#index")

Create the templates:

    <!-- polls/index.html -->
    <ol>
      {% for poll in self.polls %}
        <li><a href="{% url Poll#show poll.id %}">{{ poll.name }}</a></li>
      {% endfor %}
    </ol>
    <p><a href="{% url Poll#new %}">Create a poll</a></p>
    
    <!-- polls/new.html -->
    <form method="post" action="{% url Poll#create %}">
      {% csrf_token %}
      {{ self.form.as_p }}
      <input type="submit" value="Create Poll" />
    </form>
    
    <!-- polls/show.html -->
    <p>Name: {{ self.poll.name }}</p>
    <p><a href="{% url Poll#edit self.poll.id %}">Edit this poll</a></p>
    
    <!-- polls/edit.html -->
    <form method="post" action="{% url Poll#update self.poll.id %}">
      {% csrf_token %}
      {{ self.form.as_p }}
      <input type="submit" value="Update poll" />
    </form>

Set up the URLs:

    from django.conf.urls.defaults import *
    from dagny.urls import resources
    
    urlpatterns = patterns('',
        (r'^polls/', resources('polls.resources.Poll', name='Poll')),
    )

Done.


## Example Project

There’s a more comprehensive [example project][] which showcases a user
management app, built in very few lines of code on top of the standard
`django.contrib.auth` app.

  [example project]: http://github.com/zacharyvoase/dagny/tree/master/example/

To get it running:

    git clone 'git://github.com/zacharyvoase/dagny.git'
    cd dagny/
    pip install -r REQUIREMENTS  # Installs runtime requirements
    pip install -r REQUIREMENTS.test  # Installs testing requirements
    cd example/
    ./manage.py syncdb  # Creates db/development.sqlite3
    ./manage.py test users  # Runs all the tests
    ./manage.py runserver

Then just visit <http://localhost:8000/users/> to see it in action!


## License

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this
software, either in source code form or as a compiled binary, for any purpose,
commercial or non-commercial, and by any means.

In jurisdictions that recognize copyright laws, the author or authors of this
software dedicate any and all copyright interest in the software to the public
domain. We make this dedication for the benefit of the public at large and to
the detriment of our heirs and successors. We intend this dedication to be an
overt act of relinquishment in perpetuity of all present and future rights to
this software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
