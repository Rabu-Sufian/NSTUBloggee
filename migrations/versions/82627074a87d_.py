"""empty message

Revision ID: 82627074a87d
Revises: 2d6ab9ae8e1e
Create Date: 2020-06-08 21:52:58.257009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82627074a87d'
down_revision = '2d6ab9ae8e1e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("post") as batch_op:
        batch_op.drop_column('likes')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('likes', sa.INTEGER(), nullable=True))
    # ### end Alembic commands ###
