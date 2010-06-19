# The Renderer

An action comes in two parts: one part does the processing, and the other (known
as the **renderer**) returns a response to the client. This allows for
transparent content negotiation, and means you never have to write a separate
‘API’ for your site, or call `render_to_response()` at the bottom of every view
function.


## Renderer Backends

When an action is triggered by a request, the main body of the action is first
run. If this does not return a `HttpResponse` outright, the renderer kicks in
and performs content negotiation, to decide which **renderer backend** to use.
Each backend is associated with a mimetype, so the renderer will examine the
client headers and resolve a series of acceptable backends, which it will call
in decreasing order of preference until one produces a response.

There are two types of renderer backend. The most common is the
**specific renderer backend**, which is attached to a single action for a
particular mimetype. Here’s a simple example of a backend for rendering a JSON
representation of a user:

    #!python
    from dagny import Resource, action
    from django.http import HttpResponse
    from django.shortcuts import get_object_or_404
    import simplejson
    
    class User(Resource):
        
        # ... snip! ...
        
        @action
        def show(self, username):
            self.user = get_object_or_404(User, username=username)
        
        @show.render.json
        def show(self):
            return HttpResponse(content=simplejson.dumps(self.user.to_dict()),
                                mimetype='application/json')

The decorator API is inspired by Python’s built-in `property`. As you can see,
specific renderer backends are methods which accept only `self` (which will be
the resource instance). They’re typically highly coupled with the resource and
action they’re defined on; this one assumes the presence of `self.user`, for
example.

### Content Negotiation

Assume that the `User` resource is mounted at `/users/`. Now, if you fetch
`/users/zacharyvoase/`, you’ll see the `"users/show.html"` template rendered as
a HTML page. If you fetch `/users/zacharyvoase/?format=json`, however, you’ll
get a JSON representation of that user.

Dagny’s ConNeg mechanism is quite sophisticated; `webob.acceptparse` is used to
parse HTTP `Accept` headers, and these are considered alongside explicit
`format` parameters. So, you could also have passed an
`Accept: application/json` HTTP header in that last example, and it would have
worked. If you’re using `curl`, you could try the following command:

    :::bash
    curl -H"Accept: application/json" 'http://mysite.com/users/zacharyvoase/'


## Skipping Renderers

Sometimes, you will define multiple renderer backends for an action, but in a
few cases a single backend won’t be able to generate a response for that
particular request. You can indicate this by raising `dagny.renderer.Skip`:

    #!python
    from dagny.renderer import Skip
    from django.http import HttpResponse
    
    class User(Resource):
        # ... snip! ...
        
        @show.render.rdf_xml
        def show(self):
            if not hasattr(self, 'graph'):
                raise Skip
            return HttpResponse(content=self.graph.serialize(),
                                content_type='application/rdf+xml')

The renderer will literally skip over this backend and on to the next-best
preferred one. This feature *really* comes in handy when writing
[generic backends](#generic_backends), which will only be able to determine at
runtime whether they are suitable for a given action and request.


## Additional MIME types

Additional renderers for a single action are defined using the decoration syntax
(`@<action_name>.render.<format>`) as seen above, but since content negotiation
is based on mimetypes, Dagny keeps a global `dict` (`dagny.conneg.MIMETYPES`)
mapping these **shortcodes** to full mimetype strings. You can create your own
shortcodes, and use them in resource definitions:

    #!python
    from dagny.conneg import MIMETYPES
    
    MIMETYPES['rss'] = 'application/rss+xml'
    MIMETYPES['png'] = 'image/png'
    MIMETYPES.setdefault('json', 'text/javascript')

There is already a relatively extensive list of types defined; see the
[`dagny.conneg` module][dagny.conneg] for more information.

  [dagny.conneg]: http://github.com/zacharyvoase/dagny/blob/master/src/dagny/conneg.py


## Generic Backends

Dagny also supports **generic renderer backends**; these are backends attached
to a `Renderer` instance which will be available on *all* actions by default.
They are simple functions which take both the action instance and the resource
instance. For example, the HTML renderer (which every action has as standard)
looks like:

    #!python
    from dagny.action import Action
    from dagny.utils import camel_to_underscore, resource_name
    
    from django.shortcuts import render_to_response
    from django.template import RequestContext
    
    @Action.RENDERER.html
    def render_html(action, resource):
        template_path_prefix = getattr(resource, 'template_path_prefix', "")
        resource_label = camel_to_underscore(resource_name(resource))
        template_name = "%s%s/%s.html" % (template_path_prefix, resource_label, action.name)
        
        return render_to_response(template_name, {
          'self': resource
        }, context_instance=RequestContext(resource.request))

To go deeper, `Action.RENDERER` is a globally-shared instance of
`dagny.renderer.Renderer`, whereas the `render` attribute on actions is actually
a `BoundRenderer`. This split is what allows you to define specific backends
that just take `self` (the resource instance), and generic backends which also
take the action.

Each `BoundRenderer` has a copy of the whole set of generic backends, so you can
operate on them as if they had been defined on that action:

    :::python
    class User(Resource):
        @action
        def show(self, username):
            self.user = get_object_or_404(User, username=username)
        
        # Remove the generic HTML backend from the `show` action alone.
        del show.render['html']
        
        # Item assignment, even on a `BoundRenderer`, takes generic backend
        # functions (i.e. functions which accept both the action *and* the
        # resource).
        show.render['html'] = my_generic_html_backend


### Skipping in Generic Backends

As mentioned previously, `dagny.renderer.Skip` becomes very useful when writing
generic backends. For example, here’s a backend which produces RDF/XML
responses, but *only* if `self.graph` exists and is an instance of
`rdflib.Graph`:

    #!python
    from dagny.action import Action
    from dagny.conneg import MIMETYPES
    from dagny.renderer import Skip
    from django.http import HttpResponse
    import rdflib
    
    # This is already defined in Dagny by default.
    MIMETYPES['rdf_xml'] = 'application/rdf+xml'
    
    @Action.RENDERER.rdf_xml
    def render_rdf_xml(action, resource):
        graph = getattr(resource, 'graph', None)
        if not isinstance(graph, rdflib.Graph):
            raise Skip
        
        return HttpResponse(content=graph.serialize(format='xml'),
                            content_type='application/rdf+xml')
