# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth import models
from django.test import TestCase
from django.utils import formats
import simplejson


class UserResourceTest(TestCase):
    
    def create_user(self):
        self.user = models.User.objects.create_user("zack", "z@zacharyvoase.com", "hello")
    
    def user_json(self):
        return {
            "username": self.user.username,
            "first_name": "",
            "last_name": ""
        }
    
    def test_index(self):
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 200)
        self.assert_('<a href="/users/new/">' in response.content)
    
    def test_index_json(self):
        self.create_user()
        
        response1 = self.client.get("/users/?format=json")
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(simplejson.loads(response1.content), [self.user_json()])
        
        response2 = self.client.get("/users/", HTTP_ACCEPT="application/json")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(simplejson.loads(response2.content), [self.user_json()])
    
    def test_new(self):
        response = self.client.get("/users/new/")
        self.assertEqual(response.status_code, 200)
        self.assert_('<form method="post" action="/users/">' in response.content)
    
    def test_create(self):
        initial_user_count = models.User.objects.count()
        
        response = self.client.post("/users/", {
            "username": "zack",
            "password1": "hello",
            "password2": "hello"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/users/1/')
        
        eventual_user_count = models.User.objects.count()
        self.assertEqual(eventual_user_count, initial_user_count + 1)
    
    def test_show(self):
        self.create_user()
        
        response = self.client.get("/users/%d/" % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assert_("Username: %s" % self.user.username in response.content)
    
    def test_show_json(self):
        self.create_user()
        
        response1 = self.client.get("/users/%d/?format=json" % self.user.id)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(simplejson.loads(response1.content), self.user_json())
        
        response2 = self.client.get("/users/%d/" % self.user.id,
                                    HTTP_ACCEPT="application/json")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(simplejson.loads(response2.content), self.user_json())
    
    def test_edit(self):
        self.create_user()
        
        response = self.client.get("/users/%d/edit/" % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assert_('<form method="post" action="/users/%d/">' % self.user.id in response.content)
    
    def test_update(self):
        self.create_user()
        
        response = self.client.post("/users/%d/" % self.user.id, {
            "username": self.user.username,
            "first_name": "Zachary",
            "last_name": "Voase",
            "email": "z@zacharyvoase.com",
            "password": self.user.password,
            "last_login": formats.localize_input(datetime.datetime.now()),
            "date_joined": formats.localize_input(datetime.datetime.now()),
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/users/1/')
        
        self.user = models.User.objects.get(id=self.user.id)
        self.assertEqual(self.user.first_name, "Zachary")
        self.assertEqual(self.user.last_name, "Voase")
    
    def test_destroy(self):
        self.create_user()
        
        initial_user_count = models.User.objects.count()
        
        response = self.client.delete("/users/%d/" % self.user.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], "http://testserver/users/")
        
        eventual_user_count = models.User.objects.count()
        self.assertEqual(eventual_user_count, initial_user_count - 1)
