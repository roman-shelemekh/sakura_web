"""empty message

Revision ID: e19e693ad866
Revises: 982a24f8e026
Create Date: 2021-06-02 23:30:28.044111

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e19e693ad866'
down_revision = '982a24f8e026'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hairdresser', sa.Column('dob', sa.Date(), nullable=True))
    op.add_column('hairdresser', sa.Column('specialization', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('hairdresser', 'specialization')
    op.drop_column('hairdresser', 'dob')
    # ### end Alembic commands ###