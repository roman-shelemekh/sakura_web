"""empty message

Revision ID: a6f4b29db7fe
Revises: 1551913491aa
Create Date: 2021-06-09 13:25:22.275855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6f4b29db7fe'
down_revision = '1551913491aa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('shifts_date_id_hairdresser_id_key', 'shifts', type_='unique')
    op.create_unique_constraint(None, 'shifts', ['date_id', 'hairdresser_id', 'salon_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'shifts', type_='unique')
    op.create_unique_constraint('shifts_date_id_hairdresser_id_key', 'shifts', ['date_id', 'hairdresser_id'])
    # ### end Alembic commands ###
