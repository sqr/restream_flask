"""adding streaming

Revision ID: 34a98d26da39
Revises: 44ff3638420f
Create Date: 2020-03-06 14:56:00.388913

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34a98d26da39'
down_revision = '44ff3638420f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('streaming',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('complete', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_streaming_title'), 'streaming', ['title'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_streaming_title'), table_name='streaming')
    op.drop_table('streaming')
    # ### end Alembic commands ###
