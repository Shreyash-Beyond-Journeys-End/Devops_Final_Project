"""create jobs table

Revision ID: 0001
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None


def upgrade():
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("company", sa.String(120), nullable=False),
        sa.Column("role", sa.String(120), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="applied"),
        sa.Column("applied_on", sa.Date, nullable=False),
        sa.Column("notes", sa.Text, nullable=False, server_default=""),
    )


def downgrade():
    op.drop_table("jobs")
