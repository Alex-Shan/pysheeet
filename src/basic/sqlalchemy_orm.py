"""SQLAlchemy ORM examples and tests for pysheeet documentation."""

import pytest
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    select,
    and_,
    or_,
    func,
    DateTime,
    event,
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    relationship,
    joinedload,
)
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

# ============================================================================
# SQLAlchemy ORM 测试
# ============================================================================


class TestDeclarativeBase:
    """Test declarative model definitions."""

    def test_define_model(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        assert User.__tablename__ == "users"


class TestSession:
    """Test session operations."""

    def test_add_commit(self):
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
            user = User(name="Alice")
            session.add(user)
            session.commit()
            assert user.id == 1
        finally:
            session.close()

    def test_add_all(self):
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
            users = [User(name="Bob"), User(name="Carol")]
            session.add_all(users)
            session.commit()
            assert all(u.id is not None for u in users)
        finally:
            session.close()


class TestORMQuery:
    """Test ORM query operations."""

    def test_select_all(self):
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
            users = session.execute(select(User)).scalars().all()
            assert len(users) == 2
        finally:
            session.close()

    def test_filter_where(self):
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
                [User(name="Alice", age=30), User(name="Bob", age=25)]
            )
            session.commit()
            user = (
                session.execute(select(User).where(User.age > 28))
                .scalars()
                .first()
            )
            assert user.name == "Alice"
        finally:
            session.close()


class TestORMFilter:
    """Test ORM filter operations."""

    def test_and_filter(self):
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
                    User(name="Amy", age=35),
                ]
            )
            session.commit()
            stmt = select(User).where(
                and_(User.age >= 30, User.name.like("A%"))
            )
            users = session.execute(stmt).scalars().all()
            assert len(users) == 2
        finally:
            session.close()

    def test_or_filter(self):
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
            session.add_all(
                [User(name="Alice"), User(name="Bob"), User(name="Carol")]
            )
            session.commit()
            stmt = select(User).where(
                or_(User.name == "Alice", User.name == "Bob")
            )
            users = session.execute(stmt).scalars().all()
            assert len(users) == 2
        finally:
            session.close()

    def test_in_filter(self):
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
            session.add_all([User(age=25), User(age=30), User(age=35)])
            session.commit()
            stmt = select(User).where(User.age.in_([25, 35]))
            users = session.execute(stmt).scalars().all()
            assert len(users) == 2
        finally:
            session.close()


class TestORMUpdate:
    """Test ORM update operations."""

    def test_update_object(self):
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
            session.add(User(name="Alice"))
            session.commit()
            user = session.execute(select(User)).scalars().first()
            user.name = "Alicia"
            session.commit()
            user = session.execute(select(User)).scalars().first()
            assert user.name == "Alicia"
        finally:
            session.close()


class TestORMDelete:
    """Test ORM delete operations."""

    def test_delete_object(self):
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
            user = (
                session.execute(select(User).where(User.name == "Bob"))
                .scalars()
                .first()
            )
            session.delete(user)
            session.commit()
            users = session.execute(select(User)).scalars().all()
            assert len(users) == 1
            assert users[0].name == "Alice"
        finally:
            session.close()


class TestOneToMany:
    """Test one-to-many relationships."""

    def test_relationship(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            posts = relationship("Post", back_populates="author")

        class Post(Base):
            __tablename__ = "posts"
            id = Column(Integer, primary_key=True)
            title = Column(String(100))
            user_id = Column(Integer, ForeignKey("users.id"))
            author = relationship("User", back_populates="posts")

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            user = User(name="Alice")
            user.posts.append(Post(title="First"))
            user.posts.append(Post(title="Second"))
            session.add(user)
            session.commit()
            user = session.execute(select(User)).scalars().first()
            assert len(user.posts) == 2
        finally:
            session.close()


class TestManyToMany:
    """Test many-to-many relationships."""

    def test_relationship(self):
        Base = declarative_base()
        student_course = Table(
            "student_course",
            Base.metadata,
            Column(
                "student_id",
                Integer,
                ForeignKey("students.id"),
                primary_key=True,
            ),
            Column(
                "course_id",
                Integer,
                ForeignKey("courses.id"),
                primary_key=True,
            ),
        )

        class Student(Base):
            __tablename__ = "students"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            courses = relationship(
                "Course", secondary=student_course, back_populates="students"
            )

        class Course(Base):
            __tablename__ = "courses"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            students = relationship(
                "Student", secondary=student_course, back_populates="courses"
            )

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            math = Course(name="Math")
            physics = Course(name="Physics")
            alice = Student(name="Alice", courses=[math, physics])
            bob = Student(name="Bob", courses=[math])
            session.add_all([alice, bob])
            session.commit()
            math = (
                session.execute(select(Course).where(Course.name == "Math"))
                .scalars()
                .first()
            )
            assert len(math.students) == 2
        finally:
            session.close()


class TestSelfReferential:
    """Test self-referential relationships."""

    def test_hierarchy(self):
        Base = declarative_base()

        class Employee(Base):
            __tablename__ = "employees"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            manager_id = Column(Integer, ForeignKey("employees.id"))
            manager = relationship(
                "Employee", remote_side=[id], backref="subordinates"
            )

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            ceo = Employee(name="CEO")
            session.add(ceo)
            session.flush()
            manager = Employee(name="Manager", manager_id=ceo.id)
            session.add(manager)
            session.flush()
            worker = Employee(name="Worker", manager_id=manager.id)
            session.add(worker)
            session.commit()
            mgr = (
                session.execute(
                    select(Employee).where(Employee.name == "Manager")
                )
                .scalars()
                .first()
            )
            assert mgr.manager.name == "CEO"
            assert len(mgr.subordinates) == 1
        finally:
            session.close()


class TestCascade:
    """Test cascade delete."""

    def test_delete_orphan(self):
        Base = declarative_base()

        class Parent(Base):
            __tablename__ = "parents"
            id = Column(Integer, primary_key=True)
            children = relationship("Child", cascade="all, delete-orphan")

        class Child(Base):
            __tablename__ = "children"
            id = Column(Integer, primary_key=True)
            parent_id = Column(Integer, ForeignKey("parents.id"))

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            parent = Parent()
            parent.children = [Child(), Child()]
            session.add(parent)
            session.commit()
            session.delete(parent)
            session.commit()
            children = session.execute(select(Child)).scalars().all()
            assert len(children) == 0
        finally:
            session.close()


class TestEagerLoading:
    """Test eager loading."""

    def test_joinedload(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            posts = relationship("Post", back_populates="author")

        class Post(Base):
            __tablename__ = "posts"
            id = Column(Integer, primary_key=True)
            title = Column(String(100))
            user_id = Column(Integer, ForeignKey("users.id"))
            author = relationship("User", back_populates="posts")

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            user = User(name="Alice")
            user.posts = [Post(title="Post1"), Post(title="Post2")]
            session.add(user)
            session.commit()
            stmt = select(User).options(joinedload(User.posts))
            user = session.execute(stmt).scalars().unique().first()
            assert len(user.posts) == 2
        finally:
            session.close()


class TestHybridProperty:
    """Test hybrid properties."""

    def test_full_name(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            first_name = Column(String(50))
            last_name = Column(String(50))

            @hybrid_property
            def full_name(self):
                return f"{self.first_name} {self.last_name}"

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add(User(first_name="Alice", last_name="Smith"))
            session.commit()
            user = session.execute(select(User)).scalars().first()
            assert user.full_name == "Alice Smith"
        finally:
            session.close()


class TestEventHooks:
    """Test event hooks."""

    def test_before_insert(self):
        Base = declarative_base()

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            created_at = Column(DateTime)

        @event.listens_for(User, "before_insert")
        def set_created_at(mapper, connection, target):
            target.created_at = datetime.now()

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            user = User(name="Alice")
            session.add(user)
            session.commit()
            assert user.created_at is not None
        finally:
            session.close()
