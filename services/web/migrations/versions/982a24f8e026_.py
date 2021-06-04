"""empty message

Revision ID: 982a24f8e026
Revises: 52cca9d2281a
Create Date: 2021-06-02 13:27:09.955579

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '982a24f8e026'
down_revision = '52cca9d2281a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('calendar',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('date')
    )
    op.create_table('shifts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date_id', sa.Integer(), nullable=True),
    sa.Column('hairdresser_id', sa.Integer(), nullable=True),
    sa.Column('salon_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['date_id'], ['calendar.id'], ),
    sa.ForeignKeyConstraint(['hairdresser_id'], ['hairdresser.id'], ),
    sa.ForeignKeyConstraint(['salon_id'], ['salon.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('date_id', 'hairdresser_id')
    )
    op.alter_column('client', 'phone_number',
               existing_type=sa.VARCHAR(length=32),
               nullable=False)
    op.create_unique_constraint(None, 'client', ['phone_number'])
    op.add_column('hairdresser', sa.Column('is_available', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_admin')
    op.drop_column('hairdresser', 'is_available')
    op.drop_constraint(None, 'client', type_='unique')
    op.alter_column('client', 'phone_number',
               existing_type=sa.VARCHAR(length=32),
               nullable=True)
    op.drop_table('shifts')
    op.drop_table('calendar')
    # ### end Alembic commands ###
