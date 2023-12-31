"""update just

Revision ID: c3d0100998bb
Revises: 19de805891ec
Create Date: 2024-01-01 01:18:10.244798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d0100998bb'
down_revision: Union[str, None] = '19de805891ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
