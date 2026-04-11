from alembic import context

from app.db.database import Base, engine
import app.models

connectable = engine


def _include_object(object, name, type_, reflected, compare_to):
    if (
        type_ in {"index", "unique_constraint", "foreign_key_constraint", "check_constraint"}
        and reflected
        and compare_to is None
    ):
        return False
    return True


with connectable.connect() as connection:
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        include_schemas=True,
        autogenerate=True,
        compare_index=True,
        include_object=_include_object,
    )

    with context.begin_transaction():
        context.run_migrations()
