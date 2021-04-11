import factory
import factory.fuzzy
from sqlalchemy.orm import scoped_session

import sepal.db as db
from sepal.accessions.models import Accession, AccessionItem
from sepal.locations.models import Location
from sepal.organizations.models import Organization
from sepal.profile.models import Profile
from sepal.taxa.models import Taxon

# We want tests to have their own scoped session
Session = scoped_session(db.session_factory)


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
    rank = factory.fuzzy.FuzzyChoice(["family", "genus", "species"])


class LocationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Location
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    name = factory.fuzzy.FuzzyText()
    code = factory.fuzzy.FuzzyText()
    description = factory.fuzzy.FuzzyText()


class AccessionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Accession
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    code = factory.fuzzy.FuzzyText()


class AccessionItemFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AccessionItem
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    code = factory.fuzzy.FuzzyText()
    item_type = factory.fuzzy.FuzzyChoice(
        ["plant", "seed", "vegetative", "tissue", "other"]
    )


class ProfileFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Profile
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    email = factory.Faker("email")
