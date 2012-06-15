from sqlalchemy import (
    Column,
    Integer,
    UnicodeText,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Card(Base):
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText, unique=True)
    question = Column(UnicodeText)
    answer = Column(UnicodeText)

    def __init__(self, name, question, answer):
        self.name = name
        self.question = question
        self.answer = answer

from pyramid.security import (
    Allow,
    Everyone,
    )
class RootFactory(object):
  __acl__ = [ (Allow, Everyone, 'view'),
              (Allow, 'group:editors', 'edit')]
  def __init__(self, request):
    pass
