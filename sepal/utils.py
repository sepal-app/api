from base64 import b64encode
from functools import reduce
from urllib.parse import urljoin
from typing import List, Optional

from pydantic import Field, create_model

from sepal.accessions.models import Accession
from sepal.accessions.schema import AccessionSchema
from sepal.locations.models import Location
from sepal.locations.schema import LocationSchema
from sepal.taxa.models import Taxon
from sepal.taxa.schema import TaxonSchema

# For every mapper relationship that we want to dynamically include as a child
# in a schema then we need to map the SA mapper to its pydantic schema
mapper_schemas = {
    Accession: AccessionSchema,
    Location: LocationSchema,
    Taxon: TaxonSchema,
}


def rgetattr(obj, attr, *args):
    """Get the value of a nested attribute on obj, e.g. obj.a.b.c ."""

    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return reduce(_getattr, [obj] + attr.split("."))


def get_relationship_schema(mapper, relationship):
    """Get the default schema for a relationship on a SQLAlchemy mapper."""
    relationship_class = rgetattr(mapper, f"{relationship}.prop.mapper.class_")
    return mapper_schemas.get(relationship_class, None)


def create_schema(base_schema, mapper, include: Optional[List]):
    """Dynamically create a schema for a SQLAlchemy mapper."""
    # TODO: can we omit the mapper arg if we can look up the schema in mapper_schema
    if include is None:
        include = []

    return create_model(
        "Schema",
        **{  # type: ignore
            # TODO: set the default factory based on if this is a required field,
            # e.g. the foreign key is nullable
            field: (
                get_relationship_schema(mapper, field),
                Field(default_factory=lambda: None),
            )
            # field: (get_relationship_schema(mapper, field), default=None)
            # field: (get_relationship_schema(mapper, field), ...)
            for field in include
        },
        __base__=base_schema,
    )


def make_cursor_link(request_url: str, cursor: str, limit: int):
    encoded_cursor = b64encode(cursor.encode()).decode()
    return urljoin(str(request_url), f"?limit={limit}&cursor={encoded_cursor}")
