"""empty message

Revision ID: fdbdaea442e7
Revises: a2a7f81ce56b
Create Date: 2021-06-13 11:12:06.468191

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fdbdaea442e7'
down_revision = 'a2a7f81ce56b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('appointment', 'salon_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_constraint('appointment_salon_id_fkey', 'appointment', type_='foreignkey')
    op.drop_constraint('appointment_client_id_fkey', 'appointment', type_='foreignkey')
    op.create_foreign_key(None, 'appointment', 'salon', ['salon_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'appointment', 'client', ['client_id'], ['id'], ondelete='SET NULL')
    op.drop_constraint('service_to_appointment_appointment_id_fkey', 'service_to_appointment', type_='foreignkey')
    op.drop_constraint('service_to_appointment_service_id_fkey', 'service_to_appointment', type_='foreignkey')
    op.create_foreign_key(None, 'service_to_appointment', 'service', ['service_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'service_to_appointment', 'appointment', ['appointment_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('specialization_service_id_fkey', 'specialization', type_='foreignkey')
    op.drop_constraint('specialization_hairdresser_id_fkey', 'specialization', type_='foreignkey')
    op.create_foreign_key(None, 'specialization', 'service', ['service_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'specialization', 'hairdresser', ['hairdresser_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'specialization', type_='foreignkey')
    op.drop_constraint(None, 'specialization', type_='foreignkey')
    op.create_foreign_key('specialization_hairdresser_id_fkey', 'specialization', 'hairdresser', ['hairdresser_id'], ['id'])
    op.create_foreign_key('specialization_service_id_fkey', 'specialization', 'service', ['service_id'], ['id'])
    op.drop_constraint(None, 'service_to_appointment', type_='foreignkey')
    op.drop_constraint(None, 'service_to_appointment', type_='foreignkey')
    op.create_foreign_key('service_to_appointment_service_id_fkey', 'service_to_appointment', 'service', ['service_id'], ['id'])
    op.create_foreign_key('service_to_appointment_appointment_id_fkey', 'service_to_appointment', 'appointment', ['appointment_id'], ['id'])
    op.drop_constraint(None, 'appointment', type_='foreignkey')
    op.drop_constraint(None, 'appointment', type_='foreignkey')
    op.create_foreign_key('appointment_client_id_fkey', 'appointment', 'client', ['client_id'], ['id'])
    op.create_foreign_key('appointment_salon_id_fkey', 'appointment', 'salon', ['salon_id'], ['id'])
    op.alter_column('appointment', 'salon_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
