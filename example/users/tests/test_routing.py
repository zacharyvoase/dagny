from django.core.urlresolvers import NoReverseMatch, Resolver404, reverse, resolve
from django.test import TestCase

from users import resources


COLLECTION_METHODS = {
    'GET': 'index',
    'POST': 'create'
}
MEMBER_METHODS = {
    'GET': 'show',
    'POST': 'update',
    'PUT': 'update',
    'DELETE': 'destroy'
}
SINGLETON_METHODS = {
    'GET': 'show',
    'POST': 'update',
    'PUT': 'update',
    'DELETE': 'destroy'
}
EDIT_METHODS = {'GET': 'edit'}
NEW_METHODS = {'GET': 'new'}


class RoutingTest(TestCase):

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


class DefaultRoutingTest(RoutingTest):

    def test_index(self):
        self.assertEqual(reverse('User#index'), '/users/')
        self.assert_resolves('/users/', resources.User,
                             methods=COLLECTION_METHODS)

    def test_show(self):
        self.assertEqual(reverse('User#show', args=(1,)), '/users/1/')
        self.assert_resolves('/users/1/', resources.User,
                             '1', methods=MEMBER_METHODS)

        # Fails for invalid IDs.
        self.assertRaises(NoReverseMatch, reverse, 'User#show',
                          args=('invalid',))

    def test_new(self):
        self.assertEqual(reverse('User#new'), '/users/new/')
        self.assert_resolves('/users/new/', resources.User,
                             methods=NEW_METHODS)

    def test_edit(self):
        self.assertEqual(reverse('User#edit', args=(1,)), '/users/1/edit/')
        self.assert_resolves('/users/1/edit/', resources.User,
                             '1', methods=EDIT_METHODS)

    def test_singleton(self):
        self.assertEqual(reverse('Account#show'), '/account/')
        self.assertEqual(reverse('Account#update'), '/account/')
        self.assertEqual(reverse('Account#destroy'), '/account/')
        self.assert_resolves('/account/', resources.Account,
                             methods=SINGLETON_METHODS)

    def test_singleton_new(self):
        self.assertEqual(reverse('Account#new'), '/account/new/')
        self.assert_resolves('/account/new/', resources.Account,
                             methods=NEW_METHODS)

    def test_singleton_edit(self):
        self.assertEqual(reverse('Account#edit'), '/account/edit/')
        self.assert_resolves('/account/edit/', resources.Account,
                             methods=EDIT_METHODS)


class AtomPubRoutingTest(DefaultRoutingTest):

    def test_index(self):
        self.assertEqual(reverse('UserAtomPub#index'), '/users-atompub/')
        self.assert_resolves('/users-atompub/', resources.User,
                             methods=COLLECTION_METHODS)

    def test_show(self):
        self.assertEqual(reverse('UserAtomPub#show', args=(1,)),
                         '/users-atompub/1')
        self.assert_resolves('/users-atompub/1', resources.User,
                             '1', methods=MEMBER_METHODS)

        # Fails for invalid IDs.
        self.assertRaises(NoReverseMatch, reverse, 'UserAtomPub#show',
                          args=('invalid',))

    def test_new(self):
        self.assertEqual(reverse('UserAtomPub#new'), '/users-atompub/new')
        self.assert_resolves('/users-atompub/new', resources.User,
                             methods=NEW_METHODS)

    def test_edit(self):
        self.assertEqual(reverse('UserAtomPub#edit', args=(1,)),
                         '/users-atompub/1/edit')
        self.assert_resolves('/users-atompub/1/edit', resources.User,
                             '1', methods=EDIT_METHODS)

    def test_singleton(self):
        self.assertEqual(reverse('AccountAtomPub#show'), '/account-atompub/')
        self.assertEqual(reverse('AccountAtomPub#update'), '/account-atompub/')
        self.assertEqual(reverse('AccountAtomPub#destroy'), '/account-atompub/')
        self.assert_resolves('/account-atompub/', resources.Account,
                             methods=SINGLETON_METHODS)

    def test_singleton_new(self):
        self.assertEqual(reverse('AccountAtomPub#new'), '/account-atompub/new')
        self.assert_resolves('/account-atompub/new', resources.Account,
                             methods=NEW_METHODS)

    def test_singleton_edit(self):
        self.assertEqual(reverse('AccountAtomPub#edit'), '/account-atompub/edit')
        self.assert_resolves('/account-atompub/edit', resources.Account,
                             methods=EDIT_METHODS)


class RailsRoutingTest(DefaultRoutingTest):

    def test_index(self):
        self.assertEqual(reverse('UserRails#index'), '/users-rails')
        self.assert_resolves('/users-rails', resources.User,
                             methods=COLLECTION_METHODS)
        self.assert_resolves('/users-rails/', resources.User,
                             methods=COLLECTION_METHODS)

    def test_index_with_format(self):
        self.assertEqual(reverse('UserRails#index', kwargs={'format': '.json'}),
                         '/users-rails.json')
        self.assert_resolves('/users-rails.json', resources.User,
                             methods=COLLECTION_METHODS, format='.json')

    def test_show(self):
        self.assertEqual(reverse('UserRails#show', kwargs={'id': 1}),
                         '/users-rails/1')
        self.assert_resolves('/users-rails/1',
                             resources.User,
                             id='1', methods=MEMBER_METHODS)
        self.assert_resolves('/users-rails/1/',
                             resources.User,
                             id='1', methods=MEMBER_METHODS)

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
                             resources.User,
                             id='1', methods=MEMBER_METHODS, format='.json')

    def test_new(self):
        self.assertEqual(reverse('UserRails#new'), '/users-rails/new')
        self.assert_resolves('/users-rails/new', resources.User,
                             methods=NEW_METHODS)
        self.assert_resolves('/users-rails/new/', resources.User,
                             methods=NEW_METHODS)
        self.assertRaises(Resolver404, resolve, '/users-rails/new/foobar')
        self.assertRaises(Resolver404, resolve, '/users-rails/new.foobar')

    def test_edit(self):
        self.assertEqual(reverse('UserRails#edit', kwargs={'id': 1}),
                         '/users-rails/1/edit')
        self.assert_resolves('/users-rails/1/edit', resources.User,
                             id='1', methods=EDIT_METHODS)
        self.assert_resolves('/users-rails/1/edit/', resources.User,
                             id='1', methods=EDIT_METHODS)
        self.assertRaises(Resolver404, resolve, '/users-rails/1/edit/foobar')
        self.assertRaises(Resolver404, resolve, '/users-rails/1/edit.foobar')

    def test_singleton(self):
        self.assertEqual(reverse('AccountRails#show'), '/account-rails')
        self.assertEqual(reverse('AccountRails#update'), '/account-rails')
        self.assertEqual(reverse('AccountRails#destroy'), '/account-rails')
        self.assert_resolves('/account-rails', resources.Account,
                             methods=SINGLETON_METHODS)
        self.assert_resolves('/account-rails/', resources.Account,
                             methods=SINGLETON_METHODS)

    def test_singleton_with_format(self):
        self.assertEqual(reverse('AccountRails#show', kwargs={'format': '.json'}),
                         '/account-rails.json')

    def test_singleton_new(self):
        self.assertEqual(reverse('AccountRails#new'), '/account-rails/new')
        self.assert_resolves('/account-rails/new', resources.Account,
                             methods=NEW_METHODS)

    def test_singleton_edit(self):
        self.assertEqual(reverse('AccountRails#edit'), '/account-rails/edit')
        self.assert_resolves('/account-rails/edit', resources.Account,
                             methods=EDIT_METHODS)
