"""add quantity_unit on crop model

Revision ID: cd857eb2340d
Revises: e20e85a8effc
Create Date: 2024-09-19 17:57:38.705621

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd857eb2340d'
down_revision = 'e20e85a8effc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('crop', schema=None) as batch_op:
        batch_op.add_column(sa.Column('quantity_unit', sa.String(length=50), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('crop', schema=None) as batch_op:
        batch_op.drop_column('quantity_unit')

    # ### end Alembic commands ###
