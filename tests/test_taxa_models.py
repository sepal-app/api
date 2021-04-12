import pytest
import sqlalchemy as sa

from sepal.taxa.models import Rank, Taxon

from .fixtures import *  # noqa: F401,F403


def test_taxon_rank_enum_constraint_fails(session, org):
    with pytest.raises(sa.exc.DataError):
        taxon = Taxon(org_id=org.id, name="1234", rank="not_valid")
        session.add(taxon)
        session.commit()
    session.rollback()


def test_taxon_rank_enum_constraint(session, org):
    taxon = Taxon(org_id=org.id, name="1234", rank=Rank.Family)
    session.add(taxon)
    session.commit()
    assert isinstance(taxon.id, int)
    assert taxon.rank == Rank.Family
