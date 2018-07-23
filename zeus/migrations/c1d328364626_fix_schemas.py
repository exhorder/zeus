"""fix_schemas

Revision ID: c1d328364626
Revises: 6e7a43dc7b0e
Create Date: 2018-07-23 14:35:13.556475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c1d328364626"
down_revision = "6e7a43dc7b0e"
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "api_token_repository_access_api_token_id_fkey",
        "api_token_repository_access",
        type_="foreignkey",
    )
    op.drop_constraint(
        "api_token_repository_access_repository_id_fkey",
        "api_token_repository_access",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "api_token_repository_access",
        "api_token",
        ["api_token_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        None,
        "api_token_repository_access",
        "repository",
        ["repository_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "change_request_author_id_fkey", "change_request", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "change_request", "author", ["author_id"], ["id"], ondelete="SET NULL"
    )
    op.create_index(
        op.f("ix_repository_access_repository_id"),
        "repository_access",
        ["repository_id"],
        unique=False,
    )
    op.drop_constraint(
        "repository_access_user_id_fkey", "repository_access", type_="foreignkey"
    )
    op.drop_constraint(
        "repository_access_repository_id_fkey", "repository_access", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "repository_access", "user", ["user_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        None,
        "repository_access",
        "repository",
        ["repository_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        op.f("ix_repository_api_token_repository_id"),
        "repository_api_token",
        ["repository_id"],
        unique=False,
    )
    op.drop_constraint(
        "repository_api_token_repository_id_key", "repository_api_token", type_="unique"
    )
    op.drop_constraint("revision_author_id_fkey", "revision", type_="foreignkey")
    op.drop_constraint("revision_committer_id_fkey", "revision", type_="foreignkey")
    op.create_foreign_key(
        None, "revision", "author", ["author_id"], ["id"], ondelete="SET NULL"
    )
    op.create_foreign_key(
        None, "revision", "author", ["committer_id"], ["id"], ondelete="SET NULL"
    )
    op.drop_constraint("source_author_id_fkey", "source", type_="foreignkey")
    op.drop_constraint("source_patch_id_fkey", "source", type_="foreignkey")
    op.create_foreign_key(
        None, "source", "author", ["author_id"], ["id"], ondelete="SET NULL"
    )
    op.create_foreign_key(
        None, "source", "patch", ["patch_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "source", type_="foreignkey")
    op.drop_constraint(None, "source", type_="foreignkey")
    op.create_foreign_key(
        "source_patch_id_fkey", "source", "patch", ["patch_id"], ["id"]
    )
    op.create_foreign_key(
        "source_author_id_fkey", "source", "author", ["author_id"], ["id"]
    )
    op.drop_constraint(None, "revision", type_="foreignkey")
    op.drop_constraint(None, "revision", type_="foreignkey")
    op.create_foreign_key(
        "revision_committer_id_fkey", "revision", "author", ["committer_id"], ["id"]
    )
    op.create_foreign_key(
        "revision_author_id_fkey", "revision", "author", ["author_id"], ["id"]
    )
    op.create_unique_constraint(
        "repository_api_token_repository_id_key",
        "repository_api_token",
        ["repository_id"],
    )
    op.drop_index(
        op.f("ix_repository_api_token_repository_id"), table_name="repository_api_token"
    )
    op.drop_constraint(None, "repository_access", type_="foreignkey")
    op.drop_constraint(None, "repository_access", type_="foreignkey")
    op.create_foreign_key(
        "repository_access_repository_id_fkey",
        "repository_access",
        "repository",
        ["repository_id"],
        ["id"],
    )
    op.create_foreign_key(
        "repository_access_user_id_fkey",
        "repository_access",
        "user",
        ["user_id"],
        ["id"],
    )
    op.drop_index(
        op.f("ix_repository_access_repository_id"), table_name="repository_access"
    )
    op.drop_constraint(None, "change_request", type_="foreignkey")
    op.create_foreign_key(
        "change_request_author_id_fkey",
        "change_request",
        "author",
        ["author_id"],
        ["id"],
    )
    op.drop_constraint(None, "api_token_repository_access", type_="foreignkey")
    op.drop_constraint(None, "api_token_repository_access", type_="foreignkey")
    op.create_foreign_key(
        "api_token_repository_access_repository_id_fkey",
        "api_token_repository_access",
        "repository",
        ["repository_id"],
        ["id"],
    )
    op.create_foreign_key(
        "api_token_repository_access_api_token_id_fkey",
        "api_token_repository_access",
        "api_token",
        ["api_token_id"],
        ["id"],
    )
    # ### end Alembic commands ###
