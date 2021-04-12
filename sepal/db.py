import re

import orjson
from sqlalchemy import Column, DateTime, ForeignKey, Integer, create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base, declared_attr
from sqlalchemy.orm import Query, declarative_mixin, scoped_session, sessionmaker
from sqlalchemy.sql import expression

from sepal.settings import settings

engine = create_engine(
    settings.database_url,
    json_serializer=lambda obj: orjson.dumps(obj).decode("utf8"),
    json_deserializer=lambda obj: orjson.loads(obj),
)

session_factory = sessionmaker(
    # TODO: I think expire_on_commit would be better to avoid implicit queries
    # but it causes deadlocks when dropping the tables in the tests in SA 1.4.0b3
    #
    # expire_on_commit=False,
    bind=engine,
    future=True,
)

Session = scoped_session(session_factory)


class BaseMetaclass(DeclarativeMeta):
    @property
    def query(cls):
        return Query(cls)


Base = declarative_base(metaclass=BaseMetaclass)
metadata = Base.metadata  # used by alembic for migrations


class utcnow(expression.FunctionElement):
    """Expression to return the sql for now() in UTC."""

    type = DateTime()


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
@declarative_mixin
class IdMixin:
    """A mixin that adds a surrogate integer 'primary key' column named ``id``."""

    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)


@declarative_mixin
class TimestampMixin:
    """A mixin that adds ``created_at`` and ``updated_at`` timestamps columns."""

    __table_args__ = {"extend_existing": True}

    created_at = Column(DateTime, server_default=utcnow(), nullable=False)
    updated_at = Column(
        DateTime, server_default=utcnow(), nullable=False, onupdate=utcnow()
    )


class BaseModel(Base):  # type: ignore
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        """Return the table name of the model."""
        # return underscore cased class name
        return re.sub("(?!^)([A-Z]+)", r"_\1", cls.__name__).lower()

    # @property
    # def query(cls):
    #     return Query(cls)


class Model(TimestampMixin, IdMixin, BaseModel):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True


def reference_col(
    tablename, nullable=False, pk_name="id", foreign_key_kwargs=None, column_kwargs=None
):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    foreign_key_kwargs = foreign_key_kwargs or {}
    column_kwargs = column_kwargs or {}

    return Column(
        ForeignKey(f"{tablename}.{pk_name}", **foreign_key_kwargs),
        nullable=nullable,
        **column_kwargs,
    )
