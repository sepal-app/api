import factory
import factory.fuzzy
from sqlalchemy.orm import scoped_session, sessionmaker

import sepal.db as db
from sepal.organizations.models import Organization

Session = scoped_session(sessionmaker(bind=db.engine))


class OrganizationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Organization
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    name = factory.fuzzy.FuzzyText()
