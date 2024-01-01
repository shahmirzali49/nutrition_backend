"""add daily menu meals - autoincrement for id

Revision ID: 8181947a6f23
Revises: bb4c84beee55
Create Date: 2024-01-01 14:39:26.685216

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8181947a6f23'
down_revision: Union[str, None] = 'bb4c84beee55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create daily_menu_meals table
    op.create_table(
        'daily_menu_meals',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, nullable=False, index=True),
        sa.Column('daily_menu_id', sa.Integer, sa.ForeignKey('daily_menus.id'), primary_key=True),
        sa.Column('meal_id', sa.Integer, sa.ForeignKey('meals.id'), primary_key=True)
    )
    pass


def downgrade() -> None:
    op.drop_table('daily_menu_meals')
    pass
