import urlparse

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase


class DecoratorTest(TestCase):

    def test_login_required_when_logged_out_redirects_to_login_url(self):
        response = self.client.get('/account/')
        assert response.status_code == 302
        redirected_to = urlparse.urlparse(response['location'])
        assert redirected_to.path == settings.LOGIN_URL

    def test_login_required_when_logged_in_does_not_redirect(self):
        user = User.objects.create_user(username='someuser',
                                        email='someuser@example.com',
                                        password='password')
        assert self.client.login(username='someuser', password='password')

        response = self.client.get('/account/')
        assert response.status_code == 200
        assert response.templates[0].name == 'auth/account/show.html'

    def test_login_required_when_logged_in_dispatches_to_renderer_correctly(self):
        user = User.objects.create_user(username='someuser',
                                        email='someuser@example.com',
                                        password='password')
        assert self.client.login(username='someuser', password='password')

        response = self.client.get('/account/?format=json')
        assert response.status_code == 200
        assert response['content-type'] == 'application/json'
