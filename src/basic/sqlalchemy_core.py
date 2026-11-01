"""SQLAlchemy examples and tests for pysheeet documentation."""

from datetime import datetime
import pytest
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    select,
    insert,
    update,
    delete,
    text,
    inspect,
    func,
    and_,
    or_,
    desc,
    case,
    distinct,
    union_all,
    exists,
    DateTime,
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    relationship,
    joinedload,
    aliased,
)
from sqlalchemy.ext.hybrid import hybrid_property

# ============================================================================
# SQLAlchemy 核心测试
# ============================================================================


class TestEngine:
    """Test engine creation and database URLs."""

    def test_create_sqlite_memory(self):
        engine = create_engine("sqlite:///:memory:")
        assert engine is not None

    def test_create_sqlite_file(self, tmp_path):
        db_path = tmp_path / "test.db"
        engine = create_engine(f"sqlite:///{db_path}")
        assert engine is not None


class TestRawSQL:
    """Test raw SQL execution."""

    def test_execute_raw_sql(self):
        engine = create_engine("sqlite:///:memory:")
        with engine.connect() as conn:
            conn.execute(
                text("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            )
            conn.execute(
                text("INSERT INTO test (name) VALUES (:name)"),
                {"name": "Alice"},
            )
            conn.commit()
            result = conn.execute(text("SELECT * FROM test"))
            rows = result.fetchall()
        assert len(rows) == 1
        assert rows[0][1] == "Alice"


class TestTransaction:
    """Test transaction management."""

    def test_begin_commit(self):
        engine = create_engine("sqlite:///:memory:")
        with engine.begin() as conn:
            conn.execute(
                text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
            )
            conn.execute(text("INSERT INTO users (name) VALUES ('Bob')"))
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM users"))
            assert len(result.fetchall()) == 1


class TestMetadata:
    """Test metadata and table definitions."""

    def test_define_table(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        users = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
            Column("email", String(100)),
        )
        metadata.create_all(engine)
        assert [c.name for c in users.columns] == ["id", "name", "email"]

    def test_reflect_table(self):
        engine = create_engine("sqlite:///:memory:")
        with engine.begin() as conn:
            conn.execute(
                text(
                    "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT)"
                )
            )
        metadata = MetaData()
        metadata.reflect(bind=engine)
        assert "products" in metadata.tables


class TestInspect:
    """Test database inspection."""

    def test_get_table_names(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        Table("users", metadata, Column("id", Integer, primary_key=True))
        metadata.create_all(engine)
        inspector = inspect(engine)
        assert "users" in inspector.get_table_names()


class TestCoreInsert:
    """Test Core insert operations."""

    def test_single_insert(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        users = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )
        metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(insert(users).values(name="Alice"))
        with engine.connect() as conn:
            result = conn.execute(select(users))
            rows = result.fetchall()
        assert len(rows) == 1
        assert rows[0][1] == "Alice"

    def test_bulk_insert(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        users = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )
        metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(insert(users), [{"name": "Bob"}, {"name": "Carol"}])
        with engine.connect() as conn:
            result = conn.execute(select(users))
            assert len(result.fetchall()) == 2


class TestCoreSelect:
    """Test Core select operations."""

    def test_select_all(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        users = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
            Column("age", Integer),
        )
        metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(
                insert(users),
                [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
            )
        with engine.connect() as conn:
            result = conn.execute(select(users))
            assert len(result.fetchall()) == 2

    def test_select_where(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        users = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
            Column("age", Integer),
        )
        metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(
                insert(users),
                [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
            )
        with engine.connect() as conn:
            result = conn.execute(select(users).where(users.c.age > 28))
            rows = result.fetchall()
        assert len(rows) == 1
        assert rows[0][1] == "Alice"


class TestCoreUpdate:
    """Test Core update operations."""

    def test_update(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        users = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )
        metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(insert(users).values(name="Alice"))
            conn.execute(
                update(users)
                .where(users.c.name == "Alice")
                .values(name="Alicia")
            )
        with engine.connect() as conn:
            result = conn.execute(select(users))
            assert result.fetchone()[1] == "Alicia"


class TestCoreDelete:
    """Test Core delete operations."""

    def test_delete(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        users = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )
        metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(insert(users), [{"name": "Alice"}, {"name": "Bob"}])
            conn.execute(delete(users).where(users.c.name == "Bob"))
        with engine.connect() as conn:
            result = conn.execute(select(users))
            rows = result.fetchall()
        assert len(rows) == 1
        assert rows[0][1] == "Alice"


class TestExpressionLanguage:
    """Test SQL expression language."""

    def test_and_condition(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        users = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
            Column("age", Integer),
        )
        metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(
                insert(users),
                [
                    {"name": "Alice", "age": 30},
                    {"name": "Bob", "age": 25},
                    {"name": "Carol", "age": 35},
                ],
            )
        with engine.connect() as conn:
            stmt = select(users).where(
                and_(users.c.age > 25, users.c.age < 35)
            )
            result = conn.execute(stmt)
            rows = result.fetchall()
        assert len(rows) == 1
        assert rows[0][1] == "Alice"

    def test_or_condition(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        users = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )
        metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(
                insert(users),
                [{"name": "Alice"}, {"name": "Bob"}, {"name": "Carol"}],
            )
        with engine.connect() as conn:
            stmt = select(users).where(
                or_(users.c.name == "Alice", users.c.name == "Bob")
            )
            result = conn.execute(stmt)
            assert len(result.fetchall()) == 2

    def test_in_clause(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        users = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )
        metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(
                insert(users),
                [{"name": "Alice"}, {"name": "Bob"}, {"name": "Carol"}],
            )
        with engine.connect() as conn:
            stmt = select(users).where(users.c.name.in_(["Alice", "Carol"]))
            result = conn.execute(stmt)
            assert len(result.fetchall()) == 2


class TestCoreJoin:
    """Test Core join operations."""

    def test_join(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        users = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )
        orders = Table(
            "orders",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("user_id", Integer, ForeignKey("users.id")),
            Column("product", String(50)),
        )
        metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(insert(users), [{"name": "Alice"}, {"name": "Bob"}])
            conn.execute(
                insert(orders),
                [
                    {"user_id": 1, "product": "Book"},
                    {"user_id": 1, "product": "Pen"},
                ],
            )
        with engine.connect() as conn:
            stmt = select(users.c.name, orders.c.product).select_from(
                users.join(orders)
            )
            result = conn.execute(stmt)
            rows = result.fetchall()
        assert len(rows) == 2
        assert all(row[0] == "Alice" for row in rows)


class TestAggregate:
    """Test aggregate functions."""

    def test_count(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        sales = Table(
            "sales",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("amount", Integer),
        )
        metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(insert(sales), [{"amount": 100}, {"amount": 200}])
        with engine.connect() as conn:
            result = conn.execute(select(func.count()).select_from(sales))
            assert result.scalar() == 2

    def test_sum_group_by(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        sales = Table(
            "sales",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("product", String(50)),
            Column("amount", Integer),
        )
        metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(
                insert(sales),
                [
                    {"product": "A", "amount": 100},
                    {"product": "A", "amount": 150},
                    {"product": "B", "amount": 200},
                ],
            )
        with engine.connect() as conn:
            stmt = select(sales.c.product, func.sum(sales.c.amount)).group_by(
                sales.c.product
            )
            result = conn.execute(stmt)
            rows = dict(result.fetchall())
        assert rows["A"] == 250
        assert rows["B"] == 200


class TestDropTable:
    """Test dropping tables."""

    def test_drop_single(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        users = Table(
            "users", metadata, Column("id", Integer, primary_key=True)
        )
        metadata.create_all(engine)
        assert "users" in inspect(engine).get_table_names()
        users.drop(engine)
        assert "users" not in inspect(engine).get_table_names()

    def test_drop_all(self):
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        Table("t1", metadata, Column("id", Integer, primary_key=True))
        Table("t2", metadata, Column("id", Integer, primary_key=True))
        metadata.create_all(engine)
        assert len(inspect(engine).get_table_names()) == 2
        metadata.drop_all(engine)
        assert len(inspect(engine).get_table_names()) == 0
