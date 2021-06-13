"""empty message

Revision ID: 7ef1f539bb3b
Revises: 2da6df0b3424
Create Date: 2021-06-10 22:49:27.908109

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column


# revision identifiers, used by Alembic.
revision = '7ef1f539bb3b'
down_revision = '2da6df0b3424'
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        "discount_constraint",
        "client",
        column('discount')<=100
    )


def downgrade():
    pass
