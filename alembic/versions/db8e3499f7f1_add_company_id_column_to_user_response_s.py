"""Add company_id column to user_response_s

Revision ID: db8e3499f7f1
Revises: 354fcd1d89d4
Create Date: 2024-04-09 16:01:02.762854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db8e3499f7f1'
down_revision: Union[str, None] = '354fcd1d89d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('user_response_s',
                  sa.Column('company_id', sa.Integer(), nullable=False))

def downgrade():
    op.drop_column('user_response_s', 'company_id')
