"""fix order status and timestamps

Revision ID: 3b723cf39d0c
Revises: 9160cad17a9b
Create Date: 2026-09-20 21:07:15.671416

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b723cf39d0c'
down_revision: Union[str, Sequence[str], None] = '9160cad17a9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.DATETIME(),
            type_=sa.String(),
            existing_nullable=True,
            nullable=False,
        )

        batch_op.alter_column(
            "created_at",
            existing_type=sa.DATETIME(),
            existing_nullable=True,
            nullable=False,
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DATETIME(),
            existing_nullable=False,
            nullable=True,
        )

        batch_op.alter_column(
            "status",
            existing_type=sa.String(),
            type_=sa.DATETIME(),
            existing_nullable=False,
            nullable=True,
        )

    # ### end Alembic commands ###
