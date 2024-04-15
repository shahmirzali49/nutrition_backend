"""edited 2 UserResponses model

Revision ID: 354fcd1d89d4
Revises: 7b54675d0022
Create Date: 2024-04-08 03:30:22.483829

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '354fcd1d89d4'
down_revision: Union[str, None] = '7b54675d0022'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Önce user_id sütununu kaldırın
    op.drop_column('user_response_s', 'id')
    
    # Şimdi yeni id sütununu ekleyin
    op.add_column('user_response_s',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    )



def downgrade() -> None:
    pass
