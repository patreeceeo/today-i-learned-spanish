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
    has_permission,
    )

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Card,
    )

from .security import USERS


wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

@view_config(route_name='login', renderer='login.haml')
@forbidden_view_config(renderer='login.haml')
def login(request):
  page_name = "Login"
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
      page_name=page_name,
      )

@view_config(route_name='logout')
def logout(request):
  headers = forget(request)
  return HTTPFound(location=request.route_url('view_wiki'),
                   headers=headers)


@view_config(route_name='view_wiki')
def view_wiki(request):
  return HTTPFound(location = request.route_url('view_card', 
                                                cardid=1))

@view_config(route_name='view_card', renderer='view.haml')
def view_card(request):
  cardid = request.matchdict['cardid']
  card = DBSession.query(Card).filter_by(id=cardid).first()
  page_name = card.name
  if card is None:
    return HTTPNotFound('No such card :(')

  edit_url = request.route_url('edit_card', cardid=cardid)
  prev_card = DBSession.query(Card).filter_by(
              id=str(int(cardid)-1)).first()
  next_card = DBSession.query(Card).filter_by(
              id=str(int(cardid)+1)).first()
  if not prev_card:
    prev_card = DBSession.query(Card).order_by(Card.id.desc()).first()
  if not next_card:
    next_card = DBSession.query(Card).first()

  prev_url = request.route_url('view_card', cardid=prev_card.id)
  next_url = request.route_url('view_card', cardid=next_card.id)

  return dict(card=card, 
              edit_url=edit_url,
              prev_url=prev_url,
              next_url=next_url,
              logged_in=authenticated_userid(request),
              page_name=page_name,
              )

@view_config(route_name='add_card', renderer='edit.haml',
    permission='edit')
def add_card(request):
  cardid = request.matchdict['cardid']
  page_name = "Add Card"
  if 'form.submitted' in request.params:
    question = request.params['question']
    answer = request.params['answer']
    card = Card('', question, answer)
    DBSession.add(card)
    return HTTPFound(location=request.route_url('view_card',
                                                cardid=cardid))
  save_url = request.route_url('add_card', cardid=cardid)
  card = Card('', '', '')
  return dict(card=card, save_url=save_url,
              logged_in=authenticated_userid(request),
              page_name=page_name,
              )

@view_config(route_name='edit_card', renderer='edit.haml',
    permission='edit')
def edit_card(request):
  cardid = request.matchdict['cardid']
  card = DBSession.query(Card).filter_by(id=cardid).one()
  page_name = "Edit " + card.name
  if 'form.submitted' in request.params:
    card.question = request.params['question']
    card.answer = request.params['answer']
    DBSession.add(card)
    return HTTPFound(location = request.route_url('view_card',
                                                  cardid=cardid))
  return dict(
      card=card,
      save_url = request.route_url('edit_card', cardid=cardid),
      logged_in=authenticated_userid(request),
      page_name=page_name,
      )

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

