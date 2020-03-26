"""empty message

Revision ID: 01997d8d518c
Revises: 00ba2ef7f297
Create Date: 2020-03-12 00:30:48.934090

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01997d8d518c'
down_revision = '00ba2ef7f297'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('streaming', sa.Column('origin', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('streaming', 'origin')
    # ### end Alembic commands ###
