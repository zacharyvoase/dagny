# Reference

## Fundamental Concepts

Dagny’s fundamental unit is the **resource**. A resource is identified by, and
can be accessed at, a single HTTP URI. A resource may be singular or plural; for
example, `/users` is a collection of users, and `/users/31215` is a single user.
See the [URI documentation](/uris) for a detailed schema on Dagny’s URIs and
their behavior.

In your code, resources are defined as classes with several **actions**. An
action is essentially a method, routed to based on the request path and method,
which is in charge of processing that particular request and returning a
response. See the [Resources documentation](/resources) for a concrete
explanation of how resources and actions are defined.

Actions themselves are broken up into a main body, and a **renderer**. The body
of the action does the processing—saves/retrieves a record, or perhaps performs
some calculation. The renderer is responsible for producing a response. This
split allows for modular content negotiation: you can define multiple
**renderer backends** for an action, each of which is associated with a MIME
type. These backends will be dispatched to based on what the client has
requested; the default is to produce HTML, but you can easily write backends for
JSON, XML, RDF, or even PNG if necessary. A full reference on the renderer
system can be found in the [Renderer documentation](/renderer).
