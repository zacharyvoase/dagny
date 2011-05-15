from django.core.urlresolvers import NoReverseMatch, Resolver404, reverse, resolve
from django.test import TestCase

from users import resources


class DefaultRoutingTest(TestCase):

    def assert_resolves(self, url, func, *args, **kwargs):
        resolved = resolve(url)
        self.assertEqual(resolved.func, func)
        self.assertEqual(resolved.args, args)
        # Check that `resolved.kwargs` is a superset of `kwargs`.
        for kw, value in kwargs.items():
            self.assertIn(kw, resolved.kwargs)
            self.assertEqual(resolved.kwargs[kw], value)
        # Allows for further user-level assertions.
        return resolved

    def test_index(self):
        self.assertEqual(reverse('User#index'), '/users/')
        self.assert_resolves('/users/', resources.User, action='index')

    def test_show(self):
        self.assertEqual(reverse('User#show', args=(1,)), '/users/1/')
        self.assert_resolves('/users/1/', resources.User, '1', action='show')

        # Fails for invalid IDs.
        self.assertRaises(NoReverseMatch, reverse, 'User#show',
                          args=('invalid',))

    def test_new(self):
        self.assertEqual(reverse('User#new'), '/users/new/')
        self.assert_resolves('/users/new/', resources.User, action='new')

    def test_edit(self):
        self.assertEqual(reverse('User#edit', args=(1,)), '/users/1/edit/')
        self.assert_resolves('/users/1/edit/', resources.User, '1', action='edit')


class AtomPubRoutingTest(DefaultRoutingTest):

    def test_index(self):
        self.assertEqual(reverse('UserAtomPub#index'), '/users-atompub/')
        self.assert_resolves('/users-atompub/', resources.UserAtomPub, action='index')

    def test_show(self):
        self.assertEqual(reverse('UserAtomPub#show', args=(1,)), '/users-atompub/1')
        self.assert_resolves('/users-atompub/1', resources.UserAtomPub, '1', action='show')

        # Fails for invalid IDs.
        self.assertRaises(NoReverseMatch, reverse, 'UserAtomPub#show',
                          args=('invalid',))

    def test_new(self):
        self.assertEqual(reverse('UserAtomPub#new'), '/users-atompub/new')
        self.assert_resolves('/users-atompub/new', resources.UserAtomPub, action='new')

    def test_edit(self):
        self.assertEqual(reverse('UserAtomPub#edit', args=(1,)), '/users-atompub/1/edit')
        self.assert_resolves('/users-atompub/1/edit', resources.UserAtomPub, '1', action='edit')


class RailsRoutingTest(DefaultRoutingTest):

    def test_index(self):
        self.assertEqual(reverse('UserRails#index'), '/users-rails')
        self.assert_resolves('/users-rails', resources.UserRails, action='index')
        self.assert_resolves('/users-rails/', resources.UserRails, action='index')

    def test_index_with_format(self):
        self.assertEqual(reverse('UserRails#index', kwargs={'format': '.json'}), '/users-rails.json')
        self.assert_resolves('/users-rails.json', resources.UserRails, action='index', format='.json')

    def test_show(self):
        self.assertEqual(reverse('UserRails#show', kwargs={'id': 1}), '/users-rails/1')
        self.assert_resolves('/users-rails/1',
                             resources.UserRails,
                             id='1', action='show')

        # Fails for invalid IDs.
        self.assertRaises(NoReverseMatch, reverse, 'UserRails#show',
                          kwargs={'id': 'invalid'})
        self.assertRaises(Resolver404, resolve, '/users-rails/invalid')
        self.assertRaises(Resolver404, resolve, '/users-rails/invalid.json')
        self.assertRaises(Resolver404, resolve, '/users-rails/invalid/')

    def test_show_with_format(self):
        self.assertEqual(reverse('UserRails#show',
                                 kwargs={'id': 1, 'format': '.json'}),
                         '/users-rails/1.json')
        self.assert_resolves('/users-rails/1.json',
                             resources.UserRails,
                             id='1', action='show', format='.json')

    def test_new(self):
        self.assertEqual(reverse('UserRails#new'), '/users-rails/new')
        self.assert_resolves('/users-rails/new', resources.UserRails, action='new')
        self.assertRaises(Resolver404, resolve, '/users-rails/new/foobar')
        self.assertRaises(Resolver404, resolve, '/users-rails/new.foobar')

    def test_edit(self):
        self.assertEqual(reverse('UserRails#edit', kwargs={'id': 1}), '/users-rails/1/edit')
        self.assert_resolves('/users-rails/1/edit', resources.UserRails, id='1', action='edit')
