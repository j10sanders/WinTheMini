"""empty message

Revision ID: ab79fd10e73f
Revises: None
Create Date: 2016-06-02 01:20:46.071900

"""

# revision identifiers, used by Alembic.
revision = 'ab79fd10e73f'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('entries', sa.Column('day_rank', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('entries', 'day_rank')
    ### end Alembic commands ###