"""SQLAlchemy query recipe examples and tests for pysheeet documentation."""

import pytest
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    select,
    insert,
    func,
    desc,
    case,
    distinct,
    union_all,
    exists,
    text,
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    relationship,
    aliased,
)

# ============================================================================
# SQLAlchemy 查询配方测试
# ============================================================================


class TestOrderBy:
    """Test order by operations."""

    def test_ascending(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            age = Column(Integer)

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all(
                [
                    User(name="Alice", age=30),
                    User(name="Bob", age=25),
                    User(name="Carol", age=35),
                ]
            )
            session.commit()
            stmt = select(User).order_by(User.age)
            users = session.execute(stmt).scalars().all()
            assert [u.name for u in users] == ["Bob", "Alice", "Carol"]
        finally:
            session.close()

    def test_descending(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            age = Column(Integer)

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all([User(age=30), User(age=25), User(age=35)])
            session.commit()
            stmt = select(User).order_by(desc(User.age))
            users = session.execute(stmt).scalars().all()
            assert [u.age for u in users] == [35, 30, 25]
        finally:
            session.close()


class TestLimitOffset:
    """Test limit and offset operations."""

    def test_limit(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all([User(name=f"User{i}") for i in range(10)])
            session.commit()
            stmt = select(User).order_by(User.id).limit(3)
            users = session.execute(stmt).scalars().all()
            assert len(users) == 3
        finally:
            session.close()

    def test_offset(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all([User(name=f"User{i}") for i in range(10)])
            session.commit()
            stmt = select(User).order_by(User.id).limit(3).offset(3)
            users = session.execute(stmt).scalars().all()
            assert [u.name for u in users] == ["User3", "User4", "User5"]
        finally:
            session.close()


class TestGroupBy:
    """Test group by and aggregate operations."""

    def test_sum_group_by(self):
        Base = declarative_base()

        class Sale(Base):
            __tablename__ = "sales"
            id = Column(Integer, primary_key=True)
            product = Column(String(50))
            amount = Column(Integer)

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all(
                [
                    Sale(product="A", amount=100),
                    Sale(product="A", amount=150),
                    Sale(product="B", amount=200),
                ]
            )
            session.commit()
            stmt = select(Sale.product, func.sum(Sale.amount)).group_by(
                Sale.product
            )
            results = dict(session.execute(stmt).fetchall())
            assert results["A"] == 250
            assert results["B"] == 200
        finally:
            session.close()

    def test_having(self):
        Base = declarative_base()

        class Sale(Base):
            __tablename__ = "sales"
            id = Column(Integer, primary_key=True)
            product = Column(String(50))

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all(
                [Sale(product="A"), Sale(product="A"), Sale(product="B")]
            )
            session.commit()
            stmt = (
                select(Sale.product, func.count())
                .group_by(Sale.product)
                .having(func.count() > 1)
            )
            results = session.execute(stmt).fetchall()
            assert len(results) == 1
            assert results[0][0] == "A"
        finally:
            session.close()


class TestJoin:
    """Test join operations."""

    def test_inner_join(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        class Order(Base):
            __tablename__ = "orders"
            id = Column(Integer, primary_key=True)
            product = Column(String(50))
            user_id = Column(Integer, ForeignKey("users.id"))

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all([User(name="Alice"), User(name="Bob")])
            session.commit()
            alice = (
                session.execute(select(User).where(User.name == "Alice"))
                .scalars()
                .first()
            )
            session.add_all([Order(product="Book", user_id=alice.id)])
            session.commit()
            stmt = select(User.name, Order.product).join(Order)
            results = session.execute(stmt).fetchall()
            assert len(results) == 1
            assert results[0] == ("Alice", "Book")
        finally:
            session.close()

    def test_outer_join(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        class Order(Base):
            __tablename__ = "orders"
            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, ForeignKey("users.id"))

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all([User(name="Alice"), User(name="Bob")])
            session.commit()
            alice = (
                session.execute(select(User).where(User.name == "Alice"))
                .scalars()
                .first()
            )
            session.add(Order(user_id=alice.id))
            session.commit()
            stmt = select(User.name, Order.id).outerjoin(Order)
            results = session.execute(stmt).fetchall()
            assert len(results) == 2
        finally:
            session.close()


class TestSubquery:
    """Test subquery operations."""

    def test_scalar_subquery(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            score = Column(Integer)

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all(
                [
                    User(name="Alice", score=85),
                    User(name="Bob", score=90),
                    User(name="Carol", score=75),
                ]
            )
            session.commit()
            avg_score = select(func.avg(User.score)).scalar_subquery()
            stmt = select(User).where(User.score > avg_score)
            users = session.execute(stmt).scalars().all()
            assert len(users) == 2
        finally:
            session.close()


class TestCTE:
    """Test common table expressions."""

    def test_cte(self):
        Base = declarative_base()

        class Sale(Base):
            __tablename__ = "sales"
            id = Column(Integer, primary_key=True)
            region = Column(String(50))
            amount = Column(Integer)

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all(
                [
                    Sale(region="East", amount=100),
                    Sale(region="East", amount=200),
                    Sale(region="West", amount=150),
                ]
            )
            session.commit()
            regional_totals = (
                select(Sale.region, func.sum(Sale.amount).label("total"))
                .group_by(Sale.region)
                .cte("regional_totals")
            )
            stmt = select(regional_totals).where(regional_totals.c.total > 200)
            results = session.execute(stmt).fetchall()
            assert len(results) == 1
            assert results[0][0] == "East"
        finally:
            session.close()


class TestExists:
    """Test exists operations."""

    def test_exists(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        class Order(Base):
            __tablename__ = "orders"
            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, ForeignKey("users.id"))

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all([User(name="Alice"), User(name="Bob")])
            session.commit()
            alice = (
                session.execute(select(User).where(User.name == "Alice"))
                .scalars()
                .first()
            )
            session.add(Order(user_id=alice.id))
            session.commit()
            has_orders = exists().where(Order.user_id == User.id)
            stmt = select(User).where(has_orders)
            users = session.execute(stmt).scalars().all()
            assert len(users) == 1
            assert users[0].name == "Alice"
        finally:
            session.close()

    def test_not_exists(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        class Order(Base):
            __tablename__ = "orders"
            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, ForeignKey("users.id"))

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all([User(name="Alice"), User(name="Bob")])
            session.commit()
            alice = (
                session.execute(select(User).where(User.name == "Alice"))
                .scalars()
                .first()
            )
            session.add(Order(user_id=alice.id))
            session.commit()
            has_orders = exists().where(Order.user_id == User.id)
            stmt = select(User).where(~has_orders)
            users = session.execute(stmt).scalars().all()
            assert len(users) == 1
            assert users[0].name == "Bob"
        finally:
            session.close()


class TestUnion:
    """Test union operations."""

    def test_union_all(self):
        Base = declarative_base()

        class Customer(Base):
            __tablename__ = "customers"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        class Supplier(Base):
            __tablename__ = "suppliers"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all([Customer(name="Alice"), Customer(name="Bob")])
            session.add_all([Supplier(name="Acme"), Supplier(name="Bob")])
            session.commit()
            stmt = union_all(select(Customer.name), select(Supplier.name))
            results = [row[0] for row in session.execute(stmt)]
            assert len(results) == 4
            assert results.count("Bob") == 2
        finally:
            session.close()


class TestCase:
    """Test case expressions."""

    def test_case(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            score = Column(Integer)

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all(
                [
                    User(name="Alice", score=95),
                    User(name="Bob", score=75),
                    User(name="Carol", score=55),
                ]
            )
            session.commit()
            grade = case(
                (User.score >= 90, "A"), (User.score >= 70, "B"), else_="C"
            )
            stmt = select(User.name, grade.label("grade"))
            results = dict(session.execute(stmt).fetchall())
            assert results["Alice"] == "A"
            assert results["Bob"] == "B"
            assert results["Carol"] == "C"
        finally:
            session.close()


class TestDistinct:
    """Test distinct operations."""

    def test_distinct(self):
        Base = declarative_base()

        class Order(Base):
            __tablename__ = "orders"
            id = Column(Integer, primary_key=True)
            customer = Column(String(50))

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all(
                [
                    Order(customer="Alice"),
                    Order(customer="Alice"),
                    Order(customer="Bob"),
                ]
            )
            session.commit()
            stmt = select(Order.customer).distinct()
            results = session.execute(stmt).fetchall()
            assert len(results) == 2
        finally:
            session.close()

    def test_count_distinct(self):
        Base = declarative_base()

        class Order(Base):
            __tablename__ = "orders"
            id = Column(Integer, primary_key=True)
            product = Column(String(50))

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all(
                [
                    Order(product="Book"),
                    Order(product="Book"),
                    Order(product="Pen"),
                ]
            )
            session.commit()
            stmt = select(func.count(distinct(Order.product)))
            result = session.execute(stmt).scalar()
            assert result == 2
        finally:
            session.close()


class TestAliased:
    """Test aliased tables."""

    def test_aliased(self):
        Base = declarative_base()

        class Employee(Base):
            __tablename__ = "employees"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            salary = Column(Integer)

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all(
                [
                    Employee(name="Alice", salary=50000),
                    Employee(name="Bob", salary=60000),
                    Employee(name="Carol", salary=55000),
                ]
            )
            session.commit()
            alice_alias = aliased(Employee, name="alice")
            stmt = (
                select(Employee.name)
                .select_from(Employee)
                .join(alice_alias, alice_alias.name == "Alice")
                .where(Employee.salary > alice_alias.salary)
            )
            results = [row[0] for row in session.execute(stmt)]
            assert "Bob" in results
            assert "Carol" in results
            assert "Alice" not in results
        finally:
            session.close()


class TestRawSQL:
    """Test raw SQL execution."""

    def test_text(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all([User(name="Alice"), User(name="Bob")])
            session.commit()
            result = session.execute(
                text("SELECT * FROM users WHERE name = :name"),
                {"name": "Alice"},
            )
            rows = result.fetchall()
            assert len(rows) == 1
            assert rows[0][1] == "Alice"
        finally:
            session.close()
