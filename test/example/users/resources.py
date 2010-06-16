# -*- coding: utf-8 -*-

from dagny import Resource, action
from django.contrib.auth import forms, models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
import simplejson


class User(Resource):
    
    template_path_prefix = 'auth/'
    
    @action
    def index(self):
        self.users = models.User.objects.all()
    
    @index.render.json
    def index(self):
        return json_response([user_to_dict(user) for user in self.users])
    
    @action
    def new(self):
        self.form = forms.UserCreationForm()
    
    @action
    def create(self):
        self.form = forms.UserCreationForm(self.request.POST)
        if self.form.is_valid():
            self.user = self.form.save()
            return redirect('User#show', str(self.user.id))
        
        response = self.new.render()
        response.status_code = 403
        return response
    
    @action
    def show(self, user_id):
        self.user = get_object_or_404(models.User, id=int(user_id))
    
    @show.render.json
    def show(self):
        return json_response(user_to_dict(self.user))
    
    @action
    def edit(self, user_id):
        self.user = get_object_or_404(models.User, id=int(user_id))
        self.form = forms.UserChangeForm(instance=self.user)
    
    @action
    def update(self, user_id):
        self.user = get_object_or_404(models.User, id=int(user_id))
        self.form = forms.UserChangeForm(self.request.POST, instance=self.user)
        if self.form.is_valid():
            self.form.save()
            return redirect('User#show', str(self.user.id))
        
        response = self.edit.render()
        response.status_code = 403
        return response
    
    @action
    def destroy(self, user_id):
        self.user = get_object_or_404(models.User, id=int(user_id))
        self.user.delete()
        return redirect('User#index')


def json_response(data):
    return HttpResponse(content=simplejson.dumps(data),
                        content_type='application/json')

def user_to_dict(user):
    return {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name
    }
