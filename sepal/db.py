import re

from databases import Database
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Table as BaseTable,
    create_engine,
)
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base, declared_attr
from sqlalchemy.orm import Query, sessionmaker
from sqlalchemy.sql import expression

from sepal.settings import settings

engine = create_engine(settings.database_url)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = Database(settings.database_url)


class BaseMetaclass(DeclarativeMeta):
    @property
    def query(cls):
        return Query(cls)


Base = declarative_base(metaclass=BaseMetaclass)
metadata = Base.metadata  # used by alembic for migrations


class utcnow(expression.FunctionElement):
    """Expression to return the sql for now() in UTC"""

    type = DateTime()


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


def Table(table_name, *args, **kwargs):
    return BaseTable(
        table_name,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("created_at", DateTime, server_default=utcnow(), nullable=False),
        Column(
            "updated_at",
            DateTime,
            server_default=utcnow(),
            nullable=False,
            onupdate=utcnow(),
        ),
        *args,
        **kwargs,
    )


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class IdMixin(object):
    """A mixin that adds a surrogate integer 'primary key' column named ``id`` to any declarative-mapped class."""

    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        if any(
            (
                isinstance(record_id, str) and record_id.isdigit(),
                isinstance(record_id, (int, float)),
            )
        ):
            return cls.query.get(int(record_id))
        return None


class TimestampMixin:
    """A mixin that adds ``created_at`` and ``updated_at`` timestamps to a to any declarative-mapped class."""

    __table_args__ = {"extend_existing": True}

    created_at = Column(DateTime, server_default=utcnow(), nullable=False)
    updated_at = Column(
        DateTime, server_default=utcnow(), nullable=False, onupdate=utcnow()
    )


class BaseModel(Base):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
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
