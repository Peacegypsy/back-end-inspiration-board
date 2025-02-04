"""empty message

Revision ID: 476dbf543b0b
Revises: 456c575cd4a3
Create Date: 2021-07-13 11:02:51.043402

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '476dbf543b0b'
down_revision = '456c575cd4a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('board_card_id_fkey', 'board', type_='foreignkey')
    op.drop_column('board', 'card_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('board', sa.Column('card_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('board_card_id_fkey', 'board', 'card', ['card_id'], ['card_id'])
    # ### end Alembic commands ###
