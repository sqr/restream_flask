"""empty message

Revision ID: 44ff3638420f
Revises: 9cbf8d842761
Create Date: 2020-02-29 17:59:50.478932

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44ff3638420f'
down_revision = '9cbf8d842761'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('complete', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_name'), 'task', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_task_name'), table_name='task')
    op.drop_table('task')
    # ### end Alembic commands ###
