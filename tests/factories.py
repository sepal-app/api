import factory
import factory.fuzzy
from sqlalchemy.orm import scoped_session, sessionmaker

import sepal.db as db
from sepal.organizations.models import Organization
from sepal.taxa.models import Taxon

Session = scoped_session(sessionmaker(bind=db.engine))


class OrganizationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Organization
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    name = factory.fuzzy.FuzzyText()


class TaxonFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Taxon
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    name = factory.fuzzy.FuzzyText()
    rank = factory.fuzzy.FuzzyText()
