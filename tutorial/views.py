import re

import code

from docutils.core import publish_parts

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )
from pyramid.response import Response
from pyramid.view import (
    view_config,
    forbidden_view_config,
    )
from pyramid.security import (
    remember,
    forget,
    authenticated_userid,
    )

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Card,
    )

from .security import USERS

wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
  login_url = request.route_url('login')
  referrer = request.url
  if referrer == login_url:
    referrer = '/' # never use the login form itself as the came_from
  came_from = request.params.get('came_from', referrer)
  message = ''
  login = ''
  password = ''
  if 'form.submitted' in request.params:
    login = request.params['login']
    password = request.params['password']
    if USERS.get(login) == password:
      headers = remember(request, login)
      return HTTPFound(location=came_from,
                       headers=headers)
    message = 'Failed login'

  return dict(
      message=message,
      url=request.application_url+'/login',
      came_from=came_from,
      login=login,
      password=password,
      )

@view_config(route_name='logout')
def logout(request):
  headers = forget(request)
  return HTTPFound(location=request.route_url('view_wiki'),
                   headers=headers)


@view_config(route_name='view_wiki')
def view_wiki(request):
  return HTTPFound(location = request.route_url('view_card', 
                                                cardname='FrontCard'))

@view_config(route_name='view_card', renderer='templates/view.pt')
def view_card(request):
  cardname = request.matchdict['cardname']
  card = DBSession.query(Card).filter_by(name=cardname).first()
  if card is None:
    return HTTPNotFound('No such card :(')

  def check(match):
    word = match.group(1)
    exists = DBSession.query(Card).filter_by(name=word).all()
    if exists:
      view_url = request.route_url('view_card', cardname=word)
      return '<a href="%s">%s</a>' % (view_url, word)
    else:
      add_url = request.route_url('add_card', cardname=word)
      return '<a href="%s">%s</a>' % (add_url, word)

  # content = publish_parts(card.question, writer_name='html')['html_body']
  # content = wikiwords.sub(check, content)
  edit_url = request.route_url('edit_card', cardname=cardname)
  return dict(card=card, edit_url=edit_url,
              logged_in=authenticated_userid(request))

@view_config(route_name='add_card', renderer='templates/edit.pt',
    permission='edit')
def add_card(request):
  name = request.matchdict['cardname']
  if 'form.submitted' in request.params:
    question = request.params['question']
    answer = request.answer['answer']
    card = Card(name, question)
    DBSession.add(card)
    return HTTPFound(location=request.route_url('view_card',
                                                cardname=name))
  save_url = request.route_url('add_card', cardname=name)
  card = Card('', '')
  return dict(card=card, save_url=save_url,
              logged_in=authenticated_userid(request))

@view_config(route_name='edit_card', renderer='templates/edit.pt',              permission='edit')
def edit_card(request):
  name = request.matchdict['cardname']
  card = DBSession.query(Card).filter_by(name=name).one()
  if 'form.submitted' in request.params:
    card.question = request.params['question']
    card.answer = request.params['answer']
    DBSession.add(card)
    return HTTPFound(location = request.route_url('view_card',
                                                  cardname=name))
  return dict(
      card=card,
      save_url = request.route_url('edit_card', cardname=name),
      logged_in=authenticated_userid(request))

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_tutorial_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

