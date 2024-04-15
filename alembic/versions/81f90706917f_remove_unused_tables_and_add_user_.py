"""Remove unused tables and add user_responses

Revision ID: 81f90706917f
Revises: 8181947a6f23
Create Date: 2024-04-07 22:49:34.406854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81f90706917f'
down_revision: Union[str, None] = '8181947a6f23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Yorum satırına alınan tabloları silme
    op.drop_table('daily_menu_meals')
    op.drop_table('meal_preferences')
    op.drop_table('user_responses')

    # Yeni UserResponses tablosunu ekleme


    
    op.create_table(
        'user_response_s',
        sa.Column('user_id', sa.String(), nullable=False, primary_key=True),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('gender', sa.Integer(), nullable=False),
        sa.Column('activity_status', sa.Integer(), nullable=False),
        sa.Column('marital_status', sa.Integer(), nullable=False),
        sa.Column('prefers_kofte', sa.Integer(), nullable=False),
        sa.Column('prefers_kebab_guvec', sa.Integer(), nullable=False),
        sa.Column('prefers_et_kizartma', sa.Integer(), nullable=False),
        sa.Column('prefers_tavuk', sa.Integer(), nullable=False),
        sa.Column('prefers_balik', sa.Integer(), nullable=False),
        sa.Column('prefers_sebze', sa.Integer(), nullable=False),
        sa.Column('prefers_zeytinyagli', sa.Integer(), nullable=False),
        sa.Column('prefers_etli_sebze', sa.Integer(), nullable=False),
        sa.Column('prefers_corba', sa.Integer(), nullable=False),
        sa.Column('prefers_pilav', sa.Integer(), nullable=False),
        sa.Column('prefers_borek', sa.Integer(), nullable=False),
        sa.Column('prefers_makarna_eriste', sa.Integer(), nullable=False),
        sa.Column('prefers_salata_soguk', sa.Integer(), nullable=False),
        sa.Column('prefers_tatli', sa.Integer(), nullable=False),
        sa.Column('prefers_icecek', sa.Integer(), nullable=False),
        sa.Column('prefers_meyve', sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    pass
