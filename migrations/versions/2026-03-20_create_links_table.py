"""create_links_table

Revision ID: a2194fc1f9e7
Revises: 
Create Date: 2026-03-20 19:53:27.373806

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2194fc1f9e7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "links",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("short_id", sa.String(length=20), nullable=False),
        sa.Column("original_url", sa.Text(), nullable=False),
        sa.Column("clicks", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('utc', now())"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_links_short_id", "links", ["short_id"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_links_short_id", table_name="links")
    op.drop_table("links")
