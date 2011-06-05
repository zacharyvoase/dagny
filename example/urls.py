# -*- coding: utf-8 -*-

from dagny.urls import resources, resource, rails, atompub
from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^users/', resources('users.resources.User', name='User')),

    # Stub routes for the routing tests.
    (r'^users-atompub/', atompub.resources('users.resources.UserAtomPub', name='UserAtomPub')),
    (r'^users-rails', rails.resources('users.resources.UserRails', name='UserRails')),

    (r'^account/', resource('users.resources.Account', name='Account')),

    (r'^admin/', include(admin.site.urls)),
)
