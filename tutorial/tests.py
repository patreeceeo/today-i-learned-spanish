import unittest
import transaction
from pyramid import testing

def _initTestingDB():
    from sqlalchemy import create_engine
    from tutorial.models import (
        DBSession,
        Card,
        Base
        )
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    with transaction.manager:
        model = Card('FrontCard', 'This is the front card')
        DBSession.add(model)
    return DBSession

def _registerRoutes(config):
    config.add_route('view_card', '{cardname}')
    config.add_route('edit_card', '{cardname}/edit_card')
    config.add_route('add_card', 'add_card/{cardname}')


class CardModelTests(unittest.TestCase):

    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        self.session.remove()

    def _getTargetClass(self):
        from tutorial.models import Card
        return Card

    def _makeOne(self, name='SomeName', question='guess what?', answer='chicken butt'):
        return self._getTargetClass()(name, question, answer)

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.name, 'SomeName')
        self.assertEqual(instance.question, 'guess what?', 'chicken butt')

class ViewWikiTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, request):
        from tutorial.views import view_wiki
        return view_wiki(request)

    def test_it(self):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        response = self._callFUT(request)
        self.assertEqual(response.location, 'http://example.com/FrontCard')

class ViewCardTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def _callFUT(self, request):
        from tutorial.views import view_card
        return view_card(request)

    def test_it(self):
        from tutorial.models import Card
        request = testing.DummyRequest()
        request.matchdict['cardname'] = 'IDoExist'
        card = Card('IDoExist', 'Hello CruelWorld IDoExist')
        self.session.add(card)
        _registerRoutes(self.config)
        info = self._callFUT(request)
        self.assertEqual(info['card'], card)
        self.assertEqual(
            info['content'],
            '<div class="document">\n'
            '<p>Hello <a href="http://example.com/add_card/CruelWorld">'
            'CruelWorld</a> '
            '<a href="http://example.com/IDoExist">'
            'IDoExist</a>'
            '</p>\n</div>\n')
        self.assertEqual(info['edit_url'],
            'http://example.com/IDoExist/edit_card')

class AddCardTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def _callFUT(self, request):
        from tutorial.views import add_card
        return add_card(request)

    def test_it_notsubmitted(self):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        request.matchdict = {'cardname':'AnotherCard'}
        info = self._callFUT(request)
        self.assertEqual(info['card'].question,'')
        self.assertEqual(info['card'].answer, '')
        self.assertEqual(info['save_url'],
                         'http://example.com/add_card/AnotherCard')

    def test_it_submitted(self):
        from tutorial.models import Card
        _registerRoutes(self.config)
        request = testing.DummyRequest({'form.submitted':True,
                                        'question':'guess what?',
                                        'answer':'chicken butt.'})
        request.matchdict = {'cardname':'AnotherCard'}
        self._callFUT(request)
        card = self.session.query(Card).filter_by(name='AnotherCard').one()
        self.assertEqual(card.question, 'guess what?')
        self.assertEqual(card.answer, 'chicken butt.')

class EditCardTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def _callFUT(self, request):
        from tutorial.views import edit_card
        return edit_card(request)

    def test_it_notsubmitted(self):
        from tutorial.models import Card
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        request.matchdict = {'cardname':'abc'}
        card = Card('abc', 'hello')
        self.session.add(card)
        info = self._callFUT(request)
        self.assertEqual(info['card'], card)
        self.assertEqual(info['save_url'],
            'http://example.com/abc/edit_card')

    def test_it_submitted(self):
        from tutorial.models import Card
        _registerRoutes(self.config)
        request = testing.DummyRequest({'form.submitted':True,
          'question':'guess what?', 'answer':'chicken butt.'})
        request.matchdict = {'cardname':'abc'}
        card = Card('abc', 'hello')
        self.session.add(card)
        response = self._callFUT(request)
        self.assertEqual(response.location, 'http://example.com/abc')
        self.assertEqual(card.question, 'guess what?')
        self.assertEqual(card.answer, 'chicken butt.')

class FunctionalTests(unittest.TestCase):

    viewer_login = '/login?login=viewer&password=viewer' \
                   '&came_from=FrontCard&form.submitted=Login'
    viewer_wrong_login = '/login?login=viewer&password=incorrect' \
                   '&came_from=FrontCard&form.submitted=Login'
    editor_login = '/login?login=editor&password=editor' \
                   '&came_from=FrontCard&form.submitted=Login'

    def setUp(self):
        from tutorial import main
        settings = { 'sqlalchemy.url': 'sqlite://'}
        app = main({}, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
        _initTestingDB()

    def tearDown(self):
        del self.testapp
        from tutorial.models import DBSession
        DBSession.remove()

    def test_root(self):
        res = self.testapp.get('/', status=302)
        self.assertEqual(res.location, 'http://localhost/FrontCard')

    def test_FrontCard(self):
        res = self.testapp.get('/FrontCard', status=200)
        self.assertTrue(b'FrontCard' in res.body)

    def test_unexisting_card(self):
        self.testapp.get('/SomeCard', status=404)

    def test_successful_log_in(self):
        res = self.testapp.get(self.viewer_login, status=302)
        self.assertEqual(res.location, 'http://localhost/FrontCard')

    def test_failed_log_in(self):
        res = self.testapp.get(self.viewer_wrong_login, status=200)
        self.assertTrue(b'login' in res.body)

    def test_logout_link_present_when_logged_in(self):
        self.testapp.get(self.viewer_login, status=302)
        res = self.testapp.get('/FrontCard', status=200)
        self.assertTrue(b'Logout' in res.body)

    def test_logout_link_not_present_after_logged_out(self):
        self.testapp.get(self.viewer_login, status=302)
        self.testapp.get('/FrontCard', status=200)
        res = self.testapp.get('/logout', status=302)
        self.assertTrue(b'Logout' not in res.body)

    def test_anonymous_user_cannot_edit(self):
        res = self.testapp.get('/FrontCard/edit_card', status=200)
        self.assertTrue(b'Login' in res.body)

    def test_anonymous_user_cannot_add(self):
        res = self.testapp.get('/add_card/NewCard', status=200)
        self.assertTrue(b'Login' in res.body)

    def test_viewer_user_cannot_edit(self):
        self.testapp.get(self.viewer_login, status=302)
        res = self.testapp.get('/FrontCard/edit_card', status=200)
        self.assertTrue(b'Login' in res.body)

    def test_viewer_user_cannot_add(self):
        self.testapp.get(self.viewer_login, status=302)
        res = self.testapp.get('/add_card/NewCard', status=200)
        self.assertTrue(b'Login' in res.body)

    def test_editors_member_user_can_edit(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/FrontCard/edit_card', status=200)
        self.assertTrue(b'Editing' in res.body)

    def test_editors_member_user_can_add(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/add_card/NewCard', status=200)
        self.assertTrue(b'Editing' in res.body)

    def test_editors_member_user_can_view(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/FrontCard', status=200)
        self.assertTrue(b'FrontCard' in res.body)
