"""Add is_trial to user

Revision ID: 4facbbe03f11
Revises: 95340b761111
Create Date: 2024-06-21 10:28:06.565731

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4facbbe03f11'
down_revision: Union[str, None] = '95340b761111'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_trial', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_trial')
    # ### end Alembic commands ###
