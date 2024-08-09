"""Init

Revision ID: 3d240c6791ef
Revises: 
Create Date: 2024-08-09 16:47:26.121613

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d240c6791ef'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('protocol',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('server',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=140), nullable=True),
    sa.Column('ip', sa.String(length=100), nullable=True),
    sa.Column('port_panel', sa.String(length=5), nullable=True),
    sa.Column('port_key', sa.String(length=5), nullable=True),
    sa.Column('short_id', sa.String(length=10), nullable=True),
    sa.Column('public_key', sa.String(length=100), nullable=True),
    sa.Column('vless_inbound_id', sa.Integer(), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.Column('uri_path', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('description', sa.String(length=1024), nullable=True),
    sa.Column('user_count', sa.BigInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tariff',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=140), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('days', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=1024), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tg_id', sa.BigInteger(), nullable=False),
    sa.Column('subscription', sa.String(length=1024), nullable=False),
    sa.Column('username', sa.String(length=1024), nullable=False),
    sa.Column('full_name', sa.String(length=1024), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('protocol_id', sa.Integer(), nullable=True),
    sa.Column('tariff_id', sa.Integer(), nullable=True),
    sa.Column('server_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_trial', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('registered_at', sa.TIMESTAMP(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['protocol_id'], ['protocol.id'], ),
    sa.ForeignKeyConstraint(['server_id'], ['server.id'], ),
    sa.ForeignKeyConstraint(['tariff_id'], ['tariff.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tg_id')
    )
    op.create_table('client',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('server_id', sa.Integer(), nullable=True),
    sa.Column('is_enabled', sa.Boolean(), nullable=False),
    sa.Column('paid_until', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['server_id'], ['server.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('amount', sa.String(length=50), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('tariff_id', sa.Integer(), nullable=True),
    sa.Column('outstanding_balance', sa.Integer(), nullable=True),
    sa.Column('payment_uuid', sa.String(length=128), nullable=False),
    sa.Column('payment_url', sa.String(length=300), nullable=False),
    sa.Column('status', sa.Enum('succeeded', 'created', name='statusenum'), nullable=False),
    sa.ForeignKeyConstraint(['tariff_id'], ['tariff.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payment')
    op.drop_table('client')
    op.drop_table('user')
    op.drop_table('tariff')
    op.drop_table('server')
    op.drop_table('protocol')
    # ### end Alembic commands ###