"""drop profile username

Revision ID: 1d0c1f97e73b
Revises: 32a393db7b92
Create Date: 2020-11-28 13:48:03.257247

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d0c1f97e73b'
down_revision = '32a393db7b92'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('profile', 'username')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('profile', sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###