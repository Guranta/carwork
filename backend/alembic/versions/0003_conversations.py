"""conversation + message tables

Revision ID: 0003_conversations
Revises: 0002_policies_shops
Create Date: 2026-06-25

"""

from alembic import op

revision = "0003_conversations"
down_revision = "0002_policies_shops"
branch_labels = None
depends_on = None


def upgrade() -> None:
    from app.db.base import Base
    from app.models.conversation import Conversation, Message

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, tables=[Conversation.__table__, Message.__table__])


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS message")
    op.execute("DROP TABLE IF EXISTS conversation")
