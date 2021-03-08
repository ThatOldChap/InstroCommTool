"""initializing db

Revision ID: 2a2f874d61fe
Revises: 
Create Date: 2021-03-02 20:38:18.793257

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a2f874d61fe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('channel',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('_type', sa.Integer(), nullable=True),
    sa.Column('range_min', sa.Float(precision=16), nullable=True),
    sa.Column('range_max', sa.Float(precision=16), nullable=True),
    sa.Column('eu', sa.Integer(), nullable=True),
    sa.Column('full_scale_range', sa.Float(precision=16), nullable=True),
    sa.Column('full_scale_eu', sa.Integer(), nullable=True),
    sa.Column('tolerance', sa.Float(precision=8), nullable=True),
    sa.Column('tolerance_eu', sa.Integer(), nullable=True),
    sa.Column('test_range_min', sa.Float(precision=16), nullable=True),
    sa.Column('test_range_max', sa.Float(precision=16), nullable=True),
    sa.Column('test_eu', sa.Integer(), nullable=True),
    sa.Column('cal_eq_id_1', sa.Integer(), nullable=True),
    sa.Column('cal_eq_id_1_due_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_point',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('channel_id', sa.Integer(), nullable=True),
    sa.Column('input_val', sa.Float(precision=16), nullable=True),
    sa.Column('measured_val', sa.Float(precision=16), nullable=True),
    sa.Column('nominal_val', sa.Float(precision=16), nullable=True),
    sa.Column('pf', sa.Integer(), nullable=True),
    sa.Column('date_performed', sa.DateTime(), nullable=True),
    sa.Column('notes', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['channel_id'], ['channel.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_point')
    op.drop_table('channel')
    # ### end Alembic commands ###