# -*- coding: utf-8 -*-

from dagny.urls import resources, resource, rails, atompub
from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^users/', resources('users.resources.User', name='User')),

    # Stub routes for the routing tests.
    (r'^users-atompub/', atompub.resources('users.resources.User',
                                           name='UserAtomPub')),
    (r'^users-rails', rails.resources('users.resources.User',
                                      name='UserRails')),

    (r'^account/', resource('users.resources.Account', name='Account')),
    (r'^account-atompub/', atompub.resource('users.resources.Account',
                                            name='AccountAtomPub')),
    (r'^account-rails', rails.resource('users.resources.Account',
                                        name='AccountRails')),

    (r'^admin/', include(admin.site.urls)),
)
