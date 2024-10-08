"""Fix foreign key relationships

Revision ID: e20e85a8effc
Revises: 05b111b5a9d0
Create Date: 2024-09-17 17:22:44.320268

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e20e85a8effc'
down_revision = '05b111b5a9d0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('plant_stage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('crop_id', sa.Integer(), nullable=False),
    sa.Column('stage_name', sa.String(length=50), nullable=False),
    sa.Column('date_recorded', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['crop_id'], ['crop.crop_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('crop', schema=None) as batch_op:
        batch_op.add_column(sa.Column('variety', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('quantity_harvested', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('image', sa.String(length=200), nullable=True))
        batch_op.drop_column('harvest_date')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('crop', schema=None) as batch_op:
        batch_op.add_column(sa.Column('harvest_date', sa.DATE(), nullable=True))
        batch_op.drop_column('image')
        batch_op.drop_column('quantity_harvested')
        batch_op.drop_column('variety')

    op.drop_table('plant_stage')
    # ### end Alembic commands ###
