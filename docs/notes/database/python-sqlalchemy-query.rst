.. meta::
    :description lang=zh_CN: SQLAlchemy 高级查询模式，包括联接、子查询、聚合、窗口 functions 和性能优化
    :keywords: Python, SQLAlchemy, query, join, subquery, aggregate, window function, CTE, performance, optimization

==================================================================================
SQLAlchemy 查询配方（SQLAlchemy Query Recipes）
==================================================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

本节介绍 SQLAlchemy 的高级查询模式和配方。虽然 ORM 部分介绍了查询的基础知识，但实际应用程序通常需要更复杂的查询，涉及跨多个表的联接、子查询、聚合和性能优化。这些模式可帮助您编写高效的数据库查询，同时保持可读的 Python 代码。了解这些技术对于构建与关系数据库交互的可扩展应用程序至关重要。

排序（Order By）
------------------------

``order_by()`` method 按一列或多列对查询结果进行排序。直接传递列objects，或使用 ``desc()`` 进行降序排列。您可以链接多个列以进行二次排序。 SQLAlchemy还支持 ``nullsfirst()`` 和 ``nullslast()`` 来控制NULL values的排序方式，这在处理可选字段时特别有用。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select, desc
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
    ...     User(name="Carol", age=30)])
    >>> session.commit()

    >>> # 升序
    >>> stmt = select(User).order_by(User.age)
    >>> print([u.name for u in session.execute(stmt).scalars()])
    ['Bob', 'Alice', 'Carol']

    >>> # 降序排列
    >>> stmt = select(User).order_by(desc(User.age), User.name)
    >>> print([u.name for u in session.execute(stmt).scalars()])
    ['Alice', 'Carol', 'Bob']
    >>> session.close()

限制和偏移（Limit and Offset）
----------------------------------------------

使用 ``limit()`` 限制结果数量，使用 ``offset()`` 跳过行，从而启用分页。这些 methods 直接转换为 SQL、LIMIT 和 OFFSET 条款。对于大型数据集，请考虑使用键集分页（按最后看到的 ID 进行过滤）而不是基于偏移量的分页，因为 OFFSET 会因数据库必须扫描并丢弃行而在较大偏移量下变慢。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select
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
    >>> session.add_all([User(name=f"User{i}") for i in range(10)])
    >>> session.commit()

    >>> # 第一页 (3 items)
    >>> stmt = select(User).order_by(User.id).limit(3)
    >>> print([u.name for u in session.execute(stmt).scalars()])
    ['User0', 'User1', 'User2']

    >>> # 第二页
    >>> stmt = select(User).order_by(User.id).limit(3).offset(3)
    >>> print([u.name for u in session.execute(stmt).scalars()])
    ['User3', 'User4', 'User5']
    >>> session.close()

分组与聚合（Group By and Aggregates）
------------------------------------------------------------

使用 ``group_by()`` 与聚合 functions（如 ``func.count()`` 、 ``func.sum()`` 、 ``func.avg()`` 、 ``func.min()`` 和 ``func.max()`` ）进行分组计算。 ``having()`` method 在聚合后过滤组，类似于 SQL 的 HAVING 子句。当选择常规列和聚合时，所有非聚合列必须包含在 GROUP BY 子句中。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select, func
    >>> from sqlalchemy.orm import declarative_base, sessionmaker
    >>> Base = declarative_base()

    >>> class Sale(Base):
    ...     __tablename__ = "sales"
    ...     id = Column(Integer, primary_key=True)
    ...     product = Column(String(50))
    ...     amount = Column(Integer)

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> session.add_all([
    ...     Sale(product="A", amount=100),
    ...     Sale(product="A", amount=150),
    ...     Sale(product="B", amount=200),
    ...     Sale(product="B", amount=50)])
    >>> session.commit()

    >>> # 按总和分组
    >>> stmt = select(Sale.product, func.sum(Sale.amount).label("total"))\
    ...        .group_by(Sale.product)
    >>> for row in session.execute(stmt):
    ...     print(f"{row.product}: {row.total}")
    A: 250
    B: 250

    >>> # 拥有条款
    >>> stmt = select(Sale.product, func.count().label("count"))\
    ...        .group_by(Sale.product).having(func.count() > 1)
    >>> print(session.execute(stmt).fetchall())
    [('A', 2), ('B', 2)]
    >>> session.close()

连接查询（Join Queries）
------------------------------------

SQLAlchemy 提供了多种连接表的方法。对于有关系的 ORM 型号，使用 ``join()`` ，它会自动使用国外的 key。对于显式连接条件，请将条件作为第二个 argument 传递。将 ``outerjoin()`` 用于 LEFT OUTER JOIN。当 complex 连接需要时， ``select_from()`` method 指定 FROM 子句。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select
    >>> from sqlalchemy.orm import declarative_base, sessionmaker, relationship
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     orders = relationship("Order", back_populates="user")

    >>> class Order(Base):
    ...     __tablename__ = "orders"
    ...     id = Column(Integer, primary_key=True)
    ...     product = Column(String(50))
    ...     user_id = Column(Integer, ForeignKey("users.id"))
    ...     user = relationship("User", back_populates="orders")

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> alice = User(name="Alice")
    >>> alice.orders = [Order(product="Book"), Order(product="Pen")]
    >>> bob = User(name="Bob")
    >>> session.add_all([alice, bob])
    >>> session.commit()

    >>> # 内连接
    >>> stmt = select(User.name, Order.product).join(Order)
    >>> print(session.execute(stmt).fetchall())
    [('Alice', 'Book'), ('Alice', 'Pen')]

    >>> # 左外连接（包括没有订单的用户）
    >>> stmt = select(User.name, Order.product).outerjoin(Order)
    >>> print(session.execute(stmt).fetchall())
    [('Alice', 'Book'), ('Alice', 'Pen'), ('Bob', None)]
    >>> session.close()

子查询（Subqueries）
------------------------------

子查询是嵌套在其他查询中的查询。使用 ``subquery()`` 创建可在 FROM 子句中使用的子查询，或使用 ``scalar_subquery()`` 创建用于 SELECT 或 WHERE 子句中的单个 value 子查询。子查询对于 complex 过滤、计算派生的 values 或需要在主查询中引用聚合数据时非常有用。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select, func
    >>> from sqlalchemy.orm import declarative_base, sessionmaker
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     score = Column(Integer)

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> session.add_all([
    ...     User(name="Alice", score=85),
    ...     User(name="Bob", score=90),
    ...     User(name="Carol", score=75)])
    >>> session.commit()

    >>> # 标量子查询：得分高于平均水平的用户
    >>> avg_score = select(func.avg(User.score)).scalar_subquery()
    >>> stmt = select(User).where(User.score > avg_score)
    >>> print([u.name for u in session.execute(stmt).scalars()])
    ['Alice', 'Bob']
    >>> session.close()

公用表表达式 (CTE)（Common Table Expressions (CTE)）
----------------------------------------------------------------------------------------

CTE（WITH 子句）通过命名子查询来提高查询的可读性。它们对于 recursive 查询以及多次引用同一子查询时特别有用。使用 ``cte()`` 从选定的 statement 创建 CTE。 CTE 可以在 recursive 查询中引用自身，这对于组织结构图或类别树等分层数据非常有用。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select, func
    >>> from sqlalchemy.orm import declarative_base, sessionmaker
    >>> Base = declarative_base()

    >>> class Sale(Base):
    ...     __tablename__ = "sales"
    ...     id = Column(Integer, primary_key=True)
    ...     region = Column(String(50))
    ...     amount = Column(Integer)

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> session.add_all([
    ...     Sale(region="East", amount=100),
    ...     Sale(region="East", amount=200),
    ...     Sale(region="West", amount=150)])
    >>> session.commit()

    >>> # CTE 为地区总数
    >>> regional_totals = select(
    ...     Sale.region,
    ...     func.sum(Sale.amount).label("total")
    ... ).group_by(Sale.region).cte("regional_totals")

    >>> # 在主查询中使用 CTE
    >>> stmt = select(regional_totals).where(regional_totals.c.total > 200)
    >>> print(session.execute(stmt).fetchall())
    [('East', 300)]
    >>> session.close()

EXISTS 与相关子查询（Exists and Correlated Subqueries）
----------------------------------------------------------------------------------------------

``exists()`` 构造创建一个 EXISTS 子查询，如果子查询返回任何行，则返回 true。这对于检查相关记录是否存在而不加载它们非常有效。相关子查询引用外部查询中的列，允许逐行比较。使用 ``correlate()`` 显式指定子查询应与哪些表关联。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select, exists
    >>> from sqlalchemy.orm import declarative_base, sessionmaker, relationship
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))

    >>> class Order(Base):
    ...     __tablename__ = "orders"
    ...     id = Column(Integer, primary_key=True)
    ...     user_id = Column(Integer, ForeignKey("users.id"))

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> session.add_all([User(name="Alice"), User(name="Bob")])
    >>> session.commit()
    >>> alice = session.execute(select(User).where(User.name == "Alice")).scalars().first()
    >>> session.add(Order(user_id=alice.id))
    >>> session.commit()

    >>> # 有订单的用户
    >>> has_orders = exists().where(Order.user_id == User.id)
    >>> stmt = select(User).where(has_orders)
    >>> print([u.name for u in session.execute(stmt).scalars()])
    ['Alice']

    >>> # 无订单用户
    >>> stmt = select(User).where(~has_orders)
    >>> print([u.name for u in session.execute(stmt).scalars()])
    ['Bob']
    >>> session.close()

联合查询（Union Queries）
--------------------------------------

使用 ``union()`` 合并多个 SELECT statements 的结果，删除重复项。使用 ``union_all()`` 保留包括重复项在内的所有行，当您知道没有重复项或不关心它们时，速度会更快。查询必须具有与兼容的 types 相同的列数。联合对于组合来自不同表或同一表的不同筛选视图的数据非常有用。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select, union_all
    >>> from sqlalchemy.orm import declarative_base, sessionmaker
    >>> Base = declarative_base()

    >>> class Customer(Base):
    ...     __tablename__ = "customers"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))

    >>> class Supplier(Base):
    ...     __tablename__ = "suppliers"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> session.add_all([Customer(name="Alice"), Customer(name="Bob")])
    >>> session.add_all([Supplier(name="Acme"), Supplier(name="Bob")])
    >>> session.commit()

    >>> # 联合所有名称
    >>> stmt = union_all(
    ...     select(Customer.name),
    ...     select(Supplier.name))
    >>> print(sorted([row[0] for row in session.execute(stmt)]))
    ['Acme', 'Alice', 'Bob', 'Bob']
    >>> session.close()

CASE 表达式（Case Expressions）
----------------------------------------------------

``case()`` 构造为查询中的条件逻辑创建 SQL CASE expressions。它对于计算列、条件聚合和数据转换非常有用。传递（条件，结果）tuples 的 list，并使用可选的 ``else_`` 作为默认 value。大小写 expressions 可用于 SELECT、WHERE、ORDER、BY 和其他子句中。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select, case
    >>> from sqlalchemy.orm import declarative_base, sessionmaker
    >>> Base = declarative_base()

    >>> class User(Base):
    ...     __tablename__ = "users"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     score = Column(Integer)

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> session.add_all([
    ...     User(name="Alice", score=95),
    ...     User(name="Bob", score=75),
    ...     User(name="Carol", score=55)])
    >>> session.commit()

    >>> # 根据分数评分
    >>> grade = case(
    ...     (User.score >= 90, "A"),
    ...     (User.score >= 70, "B"),
    ...     else_="C")
    >>> stmt = select(User.name, grade.label("grade"))
    >>> for row in session.execute(stmt):
    ...     print(f"{row.name}: {row.grade}")
    Alice: A
    Bob: B
    Carol: C
    >>> session.close()

去重与去重计数（Distinct and Count Distinct）
------------------------------------------------------------------------

使用 ``distinct()`` 从结果中删除重复行。要计算唯一的 values，请将 ``func.count()`` 与 ``distinct()`` 组合起来。 ``distinct()`` method 可以应用于整个查询或特定列。在处理可能产生重复行的连接表时，这对于准确计数至关重要。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select, func, distinct
    >>> from sqlalchemy.orm import declarative_base, sessionmaker
    >>> Base = declarative_base()

    >>> class Order(Base):
    ...     __tablename__ = "orders"
    ...     id = Column(Integer, primary_key=True)
    ...     customer = Column(String(50))
    ...     product = Column(String(50))

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> session.add_all([
    ...     Order(customer="Alice", product="Book"),
    ...     Order(customer="Alice", product="Pen"),
    ...     Order(customer="Bob", product="Book")])
    >>> session.commit()

    >>> # 不同的客户
    >>> stmt = select(Order.customer).distinct()
    >>> print(session.execute(stmt).fetchall())
    [('Alice',), ('Bob',)]

    >>> # 计算不同产品的数量
    >>> stmt = select(func.count(distinct(Order.product)))
    >>> print(session.execute(stmt).scalar())
    2
    >>> session.close()

别名表（Aliased Tables）
--------------------------------------

使用 ``aliased()`` 为表创建别名，允许您在查询中使用不同名称多次引用同一个表。这对于需要比较同一表中的行的自联接和查询至关重要。别名创建可以具有不同连接条件和过滤器的独立引用。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select
    >>> from sqlalchemy.orm import declarative_base, sessionmaker, aliased
    >>> Base = declarative_base()

    >>> class Employee(Base):
    ...     __tablename__ = "employees"
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(50))
    ...     salary = Column(Integer)

    >>> engine = create_engine("sqlite:///:memory:")
    >>> Base.metadata.create_all(engine)
    >>> Session = sessionmaker(bind=engine)
    >>> session = Session()
    >>> session.add_all([
    ...     Employee(name="Alice", salary=50000),
    ...     Employee(name="Bob", salary=60000),
    ...     Employee(name="Carol", salary=55000)])
    >>> session.commit()

    >>> # 查找收入超过 Alice 的员工
    >>> alice_alias = aliased(Employee, name="alice")
    >>> stmt = select(Employee.name).select_from(Employee).join(
    ...     alice_alias, alice_alias.name == "Alice"
    ... ).where(Employee.salary > alice_alias.salary)
    >>> print([row[0] for row in session.execute(stmt)])
    ['Bob', 'Carol']
    >>> session.close()

批量操作（Bulk Operations）
------------------------------------------

对于插入或更新多行，批量操作比逐一添加 objects 要快得多。使用 ``session.bulk_insert_mappings()`` 进行插入，使用 ``session.bulk_update_mappings()`` 进行更新。这些 methods 绕过 ORM 的工作单元模式以获得更好的性能。为了获得更快的插入速度，请使用 Core 的 ``insert()`` 和 ``execute()`` ，传递 dictionaries 的 list。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, select, insert
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

    >>> # 带 Core 的批量插入（最快）
    >>> data = [{"name": f"User{i}"} for i in range(100)]
    >>> session.execute(insert(User), data)
    >>> session.commit()

    >>> # 核实
    >>> count = session.execute(select(func.count()).select_from(User)).scalar()
    >>> print(count)
    100
    >>> session.close()

使用 text 执行原始 SQL（Raw SQL with Text）
----------------------------------------------------------------------

当您需要执行难以用 SQLAlchemy 的构造表达的原始 SQL 时，请使用 ``text()`` 来包装 SQL strings。始终使用绑定的 parameters （ `:name` 语法）而不是 string 格式来防止 SQL 注入。 ``text()`` 构造可与 Core 查询和 ORM 查询一起使用，并且可使用 ``from_statement()`` 将结果映射到 ORM objects。

.. code-block:: python

    >>> from sqlalchemy import create_engine, Column, Integer, String, text, select
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
    >>> session.add_all([User(name="Alice"), User(name="Bob")])
    >>> session.commit()

    >>> # 原始 SQL 与 parameters
    >>> result = session.execute(
    ...     text("SELECT * FROM users WHERE name = :name"),
    ...     {"name": "Alice"})
    >>> print(result.fetchall())
    [(1, 'Alice')]

    >>> # 将原始 SQL 映射到 ORM objects
    >>> stmt = select(User).from_statement(text("SELECT * FROM users ORDER BY name"))
    >>> users = session.execute(stmt).scalars().all()
    >>> print([u.name for u in users])
    ['Alice', 'Bob']
    >>> session.close()
