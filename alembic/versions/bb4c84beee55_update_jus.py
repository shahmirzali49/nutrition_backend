"""update jus

Revision ID: bb4c84beee55
Revises: c3d0100998bb
Create Date: 2024-01-01 01:21:31.965327

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb4c84beee55'
down_revision: Union[str, None] = 'c3d0100998bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
