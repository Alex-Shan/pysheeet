.. meta::
    :description lang=zh_CN: SQLAlchemy ORM 教程，涵盖声明性模型、会话、关系和 object 关系映射模式
    :keywords: Python, SQLAlchemy, ORM, database, model, session, relationship, declarative, object-relational mapping

==================================================================
SQLAlchemy ORM 用法（SQLAlchemy ORM）
==================================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

SQLAlchemy 的 Object 关系映射器 (ORM) 提供高级抽象，允许您使用 Python classes 形式的数据库表和 objects 形式的行。 ORM 构建在 SQLAlchemy 核心之上，并添加了身份映射、工作单元模式和关系管理等功能。这种方法允许您以更加 Pythonic 的方式编写数据库代码，重点关注 objects 及其关系，而不是 SQL statements。 ORM 非常适合具有 complex 域模型的应用程序，在这些应用程序中您想要利用面向 object 的编程模式。

使用声明性基础定义模型（Define Models with Declarative Base）
------------------------------------------------------------------------------------------------

声明式系统是在 SQLAlchemy 中定义 ORM 模型的最常见方法。您使用 ``declarative_base()`` 创建 base class，然后将模型定义为 subclasses。每个模型 class 代表一个数据库表，其中 class attributes 定义列。 ``__tablename__`` attribute 指定表名称。这种方法使您的模型定义保持干净和可读，同时提供对 SQLAlchemy 功能的完全访问。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String
    >>> from sqlalchemy.orm import declarative_base
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     email = Column(String(100))
    ...     def __repr__(self):
    ...         return f"User(id={self.id}, name='{self.name}')"

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)

会话基础知识（Session Basics）
--------------------------------------------

``Session`` 是 ORM 中持久性操作的主要接口。它管理您已加载或与之关联的 objects 的 "holding zone"，并处理与数据库的通信。会话跟踪对 objects 的更改，并在您调用 ``commit()`` 时将其与数据库同步。推荐的模式是使用 ``sessionmaker`` 创建会话工厂，然后根据需要创建会话。完成后始终关闭会话以释放数据库连接。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String
    >>> from sqlalchemy.orm import declarative_base, sessionmaker
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)

    >>> session = Session()
    >>> try:
    ...     user = User(name="Alice")
    ...     session.add(user)
    ...     session.commit()
    ...     print(f"Created user with id: {user.id}")
    ... finally:
    ...     session.close()
    Created user with id: 1

添加并提交对象（Add and Commit Objects）
--------------------------------------------------------------

要将新的 objects 持久保存到数据库，请将它们添加到具有多个 objects 的 ``add()`` 或 ``add_all()`` 的会话中。 Objects 保持在 "pending" 状态，直到您调用 ``commit()`` ，这会刷新事务中数据库的所有挂起更改。如果发生错误，请调用 ``rollback()`` 撤消自上次提交以来的所有更改。提交后，自动生成的 values（如主 keys）可在 objects 上使用。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String
    >>> from sqlalchemy.orm import declarative_base, sessionmaker
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()

    >>> # 添加单个object
    >>> user1 = User(name="Alice")
    >>> session.add(user1)

    >>> # 添加多个objects
    >>> users = [User(name="Bob"), User(name="Carol")]
    >>> session.add_all(users)
    >>> session.commit()

    >>> print([u.id for u in [user1] + users])
    [1, 2, 3]
    >>> session.close()

查询对象（Query Objects）
--------------------------------------

SQLAlchemy 2.0 使用 ``select()`` 和 ``session.execute()`` 进行查询，替换旧版 ``session.query()`` API。 ``select()`` 构造接受模型 classes 或特定列。使用 ``scalars()`` 直接获取型号 instances，或使用 ``execute()`` 获取行 tuples。结果支持 iteration、list 的 ``all()`` 、第一个结果的 ``first()`` ，以及当预期只有一个结果时的 ``one()`` 。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select
    >>> from sqlalchemy.orm import declarative_base, sessionmaker
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     age = Column(Integer)

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> session.add_all([
    ...     User(name="Alice", age=30),
    ...     User(name="Bob", age=25),
    ...     User(name="Carol", age=35)])
    >>> session.commit()

    >>> # 获取所有用户
    >>> users = session.execute(select(User)).scalars().all()
    >>> print([u.name for u in users])
    ['Alice', 'Bob', 'Carol']

    >>> # Filter with where()
    >>> user = session.execute(select(User).where(User.age > 28)).scalars().first()
    >>> print(user.name)
    Alice
    >>> session.close()

过滤查询（Filter Queries）
----------------------------------------

``where()`` method 使用列比较接受过滤条件。 SQLAlchemy 重载 Python operators 生成 SQL： ``==`` 变为 ``=`` ， ``!=`` 变为 ``<>`` ，依此类推。对于 complex 条件，请使用 SQLAlchemy 中的 ``and_()`` 、 ``or_()`` 和 ``not_()`` 。列还提供 methods，如 ``in_()`` 、 ``like()`` 、 ``between()`` 、 ``is_()`` 和 ``isnot()`` ，用于 SQL 特定操作。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select, and_, or_
    >>> from sqlalchemy.orm import declarative_base, sessionmaker
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     age = Column(Integer)

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> session.add_all([
    ...     User(name="Alice", age=30),
    ...     User(name="Bob", age=25),
    ...     User(name="Carol", age=35),
    ...     User(name="Fred", age=30)])
    >>> session.commit()

    >>> # AND 状况
    >>> stmt = select(User).where(and_(User.age >= 30, User.name.like("A%")))
    >>> print([u.name for u in session.execute(stmt).scalars()])
    ['Alice']

    >>> # OR 状况
    >>> stmt = select(User).where(or_(User.name == "Alice", User.name == "Bob"))
    >>> print([u.name for u in session.execute(stmt).scalars()])
    ['Alice', 'Bob']

    >>> # IN条款
    >>> stmt = select(User).where(User.age.in_([25, 35]))
    >>> print([u.name for u in session.execute(stmt).scalars()])
    ['Bob', 'Carol']
    >>> session.close()

更新对象（Update Objects）
----------------------------------------

要更新objects，只需修改其attributes并调用 ``commit()`` 即可。会话通过称为 "dirty tracking" 的机制自动跟踪加载的 objects 的更改。当您提交时，SQLAlchemy 仅针对更改的 attributes 生成 UPDATE statements。您还可以使用 ``update()`` 进行批量更新，以提高修改多行而不将其加载到内存中时的效率。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select, update
    >>> from sqlalchemy.orm import declarative_base, sessionmaker
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> session.add(User(name="Alice"))
    >>> session.commit()

    >>> # 通过object修改更新
    >>> user = session.execute(select(User).where(User.name == "Alice")).scalars().first()
    >>> user.name = "Alicia"
    >>> session.commit()

    >>> # 验证更新
    >>> user = session.execute(select(User)).scalars().first()
    >>> print(user.name)
    Alicia
    >>> session.close()

删除对象（Delete Objects）
----------------------------------------

要删除 objects，请使用 ``session.delete()`` ，然后使用 ``commit()`` 。该会话将为 object 生成 DELETE statement。对于不加载 objects 的批量删除，请使用 ``delete()`` 构造和 ``session.execute()`` 。当 objects 有关系时，请小心级联删除 - SQLAlchemy 可以根据您的级联配置自动删除相关的 objects。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select, delete
    >>> from sqlalchemy.orm import declarative_base, sessionmaker
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> session.add_all([User(name="Alice"), User(name="Bob"), User(name="Carol")])
    >>> session.commit()

    >>> # 通过 object 删除
    >>> user = session.execute(select(User).where(User.name == "Bob")).scalars().first()
    >>> session.delete(user)
    >>> session.commit()

    >>> # 验证删除
    >>> users = session.execute(select(User)).scalars().all()
    >>> print([u.name for u in users])
    ['Alice', 'Carol']
    >>> session.close()

一对多关系（One-to-Many Relationship）
--------------------------------------------------------------

关系定义表的连接方式。一对多关系是指父表中的一条记录可以在子表中拥有多条相关记录。父端使用 ``relationship()`` ，子端使用 ``ForeignKey`` 。 ``back_populates`` parameter 创建双向关系，允许从两侧进行导航。 SQLAlchemy自动处理国外key管理。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select
    >>> from sqlalchemy.orm import declarative_base, sessionmaker, relationship
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     posts = relationship("Post", back_populates="author")

    >>> class Post(Base):
    ...     __tablename__ = "posts"
    ...     id = Column(Integer, primary_key=True)
    ...     title = Column(String(100))
    ...     user_id = Column(Integer, ForeignKey("users.id"))
    ...     author = relationship("User", back_populates="posts")

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()

    >>> user = User(name="Alice")
    >>> user.posts.append(Post(title="First Post"))
    >>> user.posts.append(Post(title="Second Post"))
    >>> session.add(user)
    >>> session.commit()

    >>> # 访问关系
    >>> user = session.execute(select(User)).scalars().first()
    >>> print([p.title for p in user.posts])
    ['First Post', 'Second Post']
    >>> session.close()

多对多关系（Many-to-Many Relationship）
----------------------------------------------------------------

多对多关系需要一个关联表，其中包含两个相关表的外部 keys。使用 ``Table`` 定义关联表，然后使用 ``relationship()`` ，其中 ``secondary`` parameter指向它。双方都可以有关系，当您在关系 collections 中添加或删除 items 时，SQLAlchemy 会自动管理关联表条目。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, select
    >>> from sqlalchemy.orm import declarative_base, sessionmaker, relationship
    >>> Base = declarative_base()

    >>> # 关联表
    >>> student_course = Table(
    ...     "student_course", Base.metadata,
    ...     Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    ...     Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True))

    >>> class Student(Base):
    ...     __tablename__ = "students"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     courses = relationship("Course", secondary=student_course, back_populates="students")

    >>> class Course(Base):
    ...     __tablename__ = "courses"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     students = relationship("Student", secondary=student_course, back_populates="courses")

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()

    >>> math = Course(name="Math")
    >>> physics = Course(name="Physics")
    >>> alice = Student(name="Alice", courses=[math, physics])
    >>> bob = Student(name="Bob", courses=[math])
    >>> session.add_all([alice, bob])
    >>> session.commit()

    >>> # 查询关系
    >>> math = session.execute(select(Course).where(Course.name == "Math")).scalars().first()
    >>> print([s.name for s in math.students])
    ['Alice', 'Bob']
    >>> session.close()

自我参照关系（Self-Referential Relationship）
--------------------------------------------------------------------------

自引用关系将表连接到自身，这对于组织结构图、类别或线索注释等分层数据很有用。使用指向同一张表的 ``ForeignKey`` 和 ``relationship()`` 与 ``remote_side`` 来指示哪一侧是"parent"。此模式允许您对树结构进行建模，其中每个节点可以有一个父节点和多个子节点。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select
    >>> from sqlalchemy.orm import declarative_base, sessionmaker, relationship
    >>> Base = declarative_base()

    >>> class Employee(Base):
    ...     __tablename__ = "employees"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     manager_id = Column(Integer, ForeignKey("employees.id"))
    ...     manager = relationship("Employee", remote_side=[id], backref="subordinates")

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()

    >>> ceo = Employee(name="CEO")
    >>> session.add(ceo)
    >>> session.flush()
    >>> manager = Employee(name="Manager", manager_id=ceo.id)
    >>> session.add(manager)
    >>> session.flush()
    >>> worker1 = Employee(name="Worker1", manager_id=manager.id)
    >>> worker2 = Employee(name="Worker2", manager_id=manager.id)
    >>> session.add_all([worker1, worker2])
    >>> session.commit()

    >>> # 导航层次结构
    >>> mgr = session.execute(select(Employee).where(Employee.name == "Manager")).scalars().first()
    >>> print(f"Manager: {mgr.name}, Boss: {mgr.manager.name}")
    Manager: Manager, Boss: CEO
    >>> print(f"Subordinates: {[e.name for e in mgr.subordinates]}")
    Subordinates: ['Worker1', 'Worker2']
    >>> session.close()

级联删除（Cascade Deletes）
------------------------------------------

级联选项控制删除或修改父项时相关 objects 发生的情况。 ``relationship()`` 上的 ``cascade`` parameter 接受级联规则的逗号分隔 string。常见选项包括 ``"all, delete-orphan"`` ，当删除父级以及从 collection 中删除子级时，该选项也会删除子级。这可确保引用完整性并防止出现孤立记录。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select
    >>> from sqlalchemy.orm import declarative_base, sessionmaker, relationship
    >>> Base = declarative_base()

    >>> class Parent(Base):
    ...     __tablename__ = "parents"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     children = relationship("Child", back_populates="parent",
    ...                            cascade="all, delete-orphan")

    >>> class Child(Base):
    ...     __tablename__ = "children"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     parent_id = Column(Integer, ForeignKey("parents.id"))
    ...     parent = relationship("Parent", back_populates="children")

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()

    >>> parent = Parent(name="Parent1")
    >>> parent.children = [Child(name="Child1"), Child(name="Child2")]
    >>> session.add(parent)
    >>> session.commit()

    >>> # 删除父项 - 子项也被删除
    >>> session.delete(parent)
    >>> session.commit()
    >>> children = session.execute(select(Child)).scalars().all()
    >>> print(len(children))
    0
    >>> session.close()

预先加载（Eager Loading）
--------------------------------------

默认情况下，SQLAlchemy 对关系使用延迟加载，当您访问相关的 objects 时执行新查询。当迭代多个 objects 时，这可能会导致 "N+1 query problem"。预加载使用 JOIN 或子查询在同一查询中获取相关的 objects。对于单个 objects 或小型 collections 使用 ``joinedload()`` ，对于较大的 collections 使用 ``selectinload()`` 以避免笛卡尔积。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select
    >>> from sqlalchemy.orm import declarative_base, sessionmaker, relationship, joinedload
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     posts = relationship("Post", back_populates="author")

    >>> class Post(Base):
    ...     __tablename__ = "posts"
    ...     id = Column(Integer, primary_key=True)
    ...     title = Column(String(100))
    ...     user_id = Column(Integer, ForeignKey("users.id"))
    ...     author = relationship("User", back_populates="posts")

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> user = User(name="Alice")
    >>> user.posts = [Post(title="Post1"), Post(title="Post2")]
    >>> session.add(user)
    >>> session.commit()

    >>> # 在单个查询中急切地加载用户的帖子
    >>> stmt = select(User).options(joinedload(User.posts))
    >>> user = session.execute(stmt).scalars().unique().first()
    >>> print([p.title for p in user.posts])  # 无需额外查询
    ['Post1', 'Post2']
    >>> session.close()

混合属性（Hybrid Properties）
----------------------------------------------

混合 properties 允许您定义在 instance 级别（在 Python 中）和 class 级别（在 SQL 查询中）工作的 Python properties。这对于您想要在数据库查询中过滤或排序的计算 attributes 非常有用。使用 ``@hybrid_property`` 、decorator 和可选的 ``@property.expression`` 来自定义 SQL expression。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select
    >>> from sqlalchemy.orm import declarative_base, sessionmaker
    >>> from sqlalchemy.ext.hybrid import hybrid_property
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     first_name = Column(String(50))
    ...     last_name = Column(String(50))
    ...
    ...     @hybrid_property
    ...     def full_name(self):
    ...         return f"{self.first_name} {self.last_name}"

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> session.add(User(first_name="Alice", last_name="Smith"))
    >>> session.commit()

    >>> user = session.execute(select(User)).scalars().first()
    >>> print(user.full_name)
    Alice Smith
    >>> session.close()

事件挂钩（Event Hooks）
----------------------------------

SQLAlchemy 提供了一个事件系统，可让您挂钩各种 ORM 操作，例如插入、更新或删除之前/之后。使用 ``@event.listens_for()`` decorator 注册事件处理程序。事件对于审核、验证、自动时间戳或触发副作用很有用。常见事件包括 ``before_insert`` 、 ``after_insert`` 、 ``before_update`` 、 ``after_update`` 、 ``before_delete`` 和 ``after_delete`` 。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, DateTime, select, event
    >>> from sqlalchemy.orm import declarative_base, sessionmaker
    >>> from datetime import datetime
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     created_at = Column(DateTime)
    ...     updated_at = Column(DateTime)

    >>> @event.listens_for(User, "before_insert")
    ... def set_created_at(mapper, connection, target):
    ...     target.created_at = datetime.now()
    ...     target.updated_at = datetime.now()

    >>> @event.listens_for(User, "before_update")
    ... def set_updated_at(mapper, connection, target):
    ...     target.updated_at = datetime.now()

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> user = User(name="Alice")
    >>> session.add(user)
    >>> session.commit()

    >>> print(user.created_at is not None)
    True
    >>> session.close()
