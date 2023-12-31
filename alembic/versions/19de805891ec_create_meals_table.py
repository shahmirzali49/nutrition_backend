"""create meals table

Revision ID: 19de805891ec
Revises: 
Create Date: 2023-12-31 23:31:38.839560

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19de805891ec'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass

def downgrade() -> None:
    pass



def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('email', sa.String, nullable=False, unique=True),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create weekly_menus table
    op.create_table(
        'weekly_menus',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('week', sa.Integer, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create daily_menus table
    op.create_table(
        'daily_menus',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('status', sa.String, nullable=False),
        sa.Column('day', sa.Integer, nullable=False),
        sa.Column('weekly_menu_id', sa.Integer, sa.ForeignKey('weekly_menus.id', ondelete='CASCADE'), nullable=False),
        sa.Column('total_energy', sa.Float, nullable=False),
        sa.Column('total_carbohydrate', sa.Float, nullable=False),
        sa.Column('total_protein', sa.Float, nullable=False),
        sa.Column('total_fat', sa.Float, nullable=False),
        sa.Column('total_fiber', sa.Float, nullable=False)
    )

    # Create meals table
    op.create_table(
        'meals',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('food', sa.String, nullable=False),
        sa.Column('price', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('color', sa.String, nullable=False),
        sa.Column('portion_weight', sa.Integer, nullable=False),
        sa.Column('consistency', sa.String, nullable=False),
        sa.Column('energy', sa.Float, nullable=False),
        sa.Column('carbohydrate', sa.Float, nullable=False),
        sa.Column('protein', sa.Float, nullable=False),
        sa.Column('fat', sa.Float, nullable=False),
        sa.Column('fiber', sa.Float, nullable=False)
    )

    # Create meal_preferences table
    op.create_table(
        'meal_preferences',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('meal_id', sa.Integer, sa.ForeignKey('meals.id')),
        sa.Column('like', sa.Boolean, nullable=True)
    )

    # Create daily_menu_meals table
    op.create_table(
        'daily_menu_meals',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('daily_menu_id', sa.Integer, sa.ForeignKey('daily_menus.id'), primary_key=True),
        sa.Column('meal_id', sa.Integer, sa.ForeignKey('meals.id'), primary_key=True)
    )

    # Create questions table
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('text', sa.String, nullable=False),
        sa.Column('type', sa.String, nullable=False)
    )

    # Create choices table
    op.create_table(
        'choices',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('question_id', sa.Integer, sa.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('text', sa.String, nullable=False)
    )

    # Create user_responses table
    op.create_table(
        'user_responses',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_id', sa.Integer, sa.ForeignKey('questions.id'), nullable=False),
        sa.Column('answer', sa.String, nullable=False)
    )
    pass

def downgrade():
    op.drop_table('user_responses')
    op.drop_table('choices')
    op.drop_table('questions')
    op.drop_table('daily_menu_meals')
    op.drop_table('meal_preferences')
    op.drop_table('meals')
    op.drop_table('daily_menus')
    op.drop_table('weekly_menus')
    op.drop_table('users')
    pass