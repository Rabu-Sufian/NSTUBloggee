"""empty message

Revision ID: a2e2fda7c3bc
Revises: 8b78c9a21f16
Create Date: 2020-06-07 15:37:05.730725

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2e2fda7c3bc'
down_revision = '8b78c9a21f16'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("comment") as batch_op:
        batch_op.alter_column('post_id', existing_type=sa.INTEGER())
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('comment', 'post_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
