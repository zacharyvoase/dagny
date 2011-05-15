# -*- coding: utf-8 -*-

from dagny.urls import resources
from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^users/', resources('users.resources.User', name='User')),

    (r'^admin/', include(admin.site.urls)),
)
