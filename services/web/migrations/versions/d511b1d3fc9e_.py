"""empty message

Revision ID: d511b1d3fc9e
Revises: 898da7aff659
Create Date: 2021-06-05 07:59:33.173749

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd511b1d3fc9e'
down_revision = '898da7aff659'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('service_name_key', 'service', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('service_name_key', 'service', ['name'])
    # ### end Alembic commands ###