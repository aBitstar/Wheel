"""add friend table

Revision ID: 20cd0620cb05
Revises: 2895a3543b55
Create Date: 2024-06-23 13:38:29.590297

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '20cd0620cb05'
down_revision = '2895a3543b55'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('friend',
    sa.Column('user1', sa.Integer(), nullable=False),
    sa.Column('user2', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('friends_since', sa.DateTime(), nullable=False),
    sa.CheckConstraint('user1 < user2', name='check_user1_less_than_user2'),
    sa.ForeignKeyConstraint(['user1'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user2'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_friend_id'), 'friend', ['id'], unique=False)
    op.add_column('friendrequest', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('user', sa.Column('created_at', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'created_at')
    op.drop_column('friendrequest', 'created_at')
    op.drop_index(op.f('ix_friend_id'), table_name='friend')
    op.drop_table('friend')
    # ### end Alembic commands ###
