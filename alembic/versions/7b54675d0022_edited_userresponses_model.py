"""edited UserResponses model

Revision ID: 7b54675d0022
Revises: 81f90706917f
Create Date: 2024-04-08 02:24:44.239590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b54675d0022'
down_revision: Union[str, None] = '81f90706917f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Kullanıcı yanıtlarını içeren tabloyu değiştirin
    op.alter_column('user_response_s', 'user_id',
               new_column_name='id',
               existing_type=sa.Integer(),
               autoincrement=True,
               nullable=False,
               unique=True,
               index=True)
    # user_id sütunu varsa ve bunu tamamen kaldırmak istiyorsanız,
    # aşağıdaki satırı yorumdan çıkarın:
    # op.drop_column('user_response_s', 'user_id')


def downgrade():
    # downgrade metodu, upgrade'ın tersini gerçekleştirmelidir.
    op.alter_column('user_response_s', 'id',
               new_column_name='user_id',
               existing_type=sa.String(),
               nullable=False, # Eğer önce nullable idiyseniz
              ) # Eğer önce indexlenmemişse


def downgrade() -> None:
    pass
