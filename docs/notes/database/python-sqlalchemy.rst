.. meta::
    :description lang=zh_CN: SQLAlchemy 核心教程，涵盖数据库连接、引擎创建、元数据、表定义和 SQL expression 语言
    :keywords: Python, SQLAlchemy, database, SQL, engine, metadata, table, connection, transaction, Core API

====================================================================
SQLAlchemy 基础知识（SQLAlchemy Basics）
====================================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

SQLAlchemy 是最流行的数据库工具包，而 Object 关系映射 (ORM) library 则适用于 Python。它提供了一整套众所周知的企业级持久性模式，专为高效、高性能的数据库访问而设计。 SQLAlchemy 分为两个主要组件：Core（低级 SQL 抽象）和 ORM（高级 object 映射）。本速查表涵盖了核心 API，它提供了 SQL Expression 语言，允许您在 Python 代码中构造 SQL statements，同时保持与数据库无关。当您需要对 SQL 查询进行细粒度控制或使用现有数据库模式时，Core 是理想的选择。

创建引擎（Create an Engine）
--------------------------------------------

``Engine`` 是任何 SQLAlchemy 应用的起点。它代表特定数据库的连接池和方言，管理连接并将 Python 代码转换为数据库特定的 SQL。 ``create_engine()`` function 采用数据库 URL，该数据库指定数据库 type、凭据、主机和数据库名称。 SQLAlchemy通过不同的方言支持SQLite、PostgreSQL、MySQL、Oracle、Microsoft SQL Server等多种数据库。

.. code-block:: python

    >>> from sqlalchemy import create_engine
    >>> # SQLite 内存数据库（非常适合测试）
    >>> engine = create_engine("sqlite:///:memory:")
    >>> # SQLite 基于文件的数据库
    >>> engine = create_engine("sqlite:///mydb.sqlite")
    >>> # PostgreSQL
    >>> engine = create_engine("postgresql://user:pass@localhost/dbname")
    >>> # MySQL
    >>> engine = create_engine("mysql+pymysql://user:pass@localhost/dbname")

数据库 URL 格式（Database URL Format）
--------------------------------------------------------------

SQLAlchemy 使用 RFC-1738 样式 URLs 来指定数据库连接。 URL 格式提供了一种标准化方法来指定所有连接 parameters，包括数据库驱动程序、身份验证凭据、主机地址、端口号和数据库名称。了解这种格式对于配置与不同数据库系统的连接至关重要。 ``make_url()`` function 可以通过编程方式解析和构造这些 URLs。

.. code-block:: python

    >>> from sqlalchemy import make_url
    >>> # 格式：方言+驱动://用户名:密码@主机:端口/数据库
    >>> url = make_url("postgresql://user:pass@localhost:5432/mydb")
    >>> url.drivername
    'postgresql'
    >>> url.username
    'user'
    >>> url.host
    'localhost'
    >>> url.database
    'mydb'

连接并执行原始 SQL（Connect and Execute Raw SQL）
--------------------------------------------------------------------------------

虽然 SQLAlchemy 鼓励使用其 SQL Expression 语言，但您也可以直接执行原始 SQL strings。这对于难以在 SQLAlchemy 的 API 中表达的 complex 查询或迁移现有 SQL 代码时非常有用。 ``text()`` function 包装原始 SQL strings 并允许 parameter 绑定以确保安全。始终使用 parameter 绑定而不是 string 格式化，以防止 SQL 注入攻击。

.. code-block:: python

    >>> from sqlalchemy import create_engine, text
    >>> engine = create_engine("sqlite:///:memory:")
    >>> with engine.connect() as conn:
    ...     conn.execute(text("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"))
    ...     conn.execute(text("INSERT INTO test (name) VALUES (:name)"), {"name": "Alice"})
    ...     conn.commit()
    ...     result = conn.execute(text("SELECT * FROM test"))
    ...     print(result.fetchall())
    [(1, 'Alice')]

事务管理（Transaction Management）
--------------------------------------------------------

事务可确保 series 的数据库操作全部成功或全部失败，从而保持数据完整性。 SQLAlchemy 提供了多种管理事务的方式：使用 ``begin()`` 隐式事务、用于自动提交/回滚的 context managers 以及使用 ``commit()`` 和 ``rollback()`` 进行手动控制。 ``begin()`` method 启动一个事务，该事务将在 exceptions 上自动回滚，并在用作 context manager 时在成功完成时提交。

.. code-block:: python

    >>> from sqlalchemy import create_engine, text
    >>> engine = create_engine("sqlite:///:memory:")
    >>> # 使用begin()进行自动提交/回滚
    >>> with engine.begin() as conn:
    ...     conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"))
    ...     conn.execute(text("INSERT INTO users (name) VALUES ('Bob')"))
    ...     # 如果没有 exception，则自动提交

    >>> # 手动交易控制
    >>> with engine.connect() as conn:
    ...     trans = conn.begin()
    ...     try:
    ...         conn.execute(text("INSERT INTO users (name) VALUES ('Carol')"))
    ...         trans.commit()
    ...     except:
    ...         trans.rollback()
    ...         raise

使用元数据定义表（Define Tables with Metadata）
--------------------------------------------------------------------------

``MetaData`` 是一个容器，保存有关数据库表和其他架构构造的信息。您可以使用 ``Table`` class 以编程方式定义表，并指定列及其 types 和约束。这种方法是 SQLAlchemy Core 的一部分，使您可以显式控制表结构。然后，元数据可以使用 ``create_all()`` 在数据库中创建所有定义的表，这会为您的数据库方言生成适当的 DDL statements。

.. code-block:: python

    >>> from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
    >>> engine = create_engine("sqlite:///:memory:")
    >>> metadata = MetaData()
    >>> users = Table(
    ...     "users", metadata,
    ...     Column("id", Integer, primary_key=True),
    ...     Column("name", String(50)),
    ...     Column("email", String(100))
    ... )
    >>> metadata.create_all(engine)
    >>> # 检查表列
    >>> [c.name for c in users.columns]
    ['id', 'name', 'email']

反射已有表（Reflect Existing Tables）
------------------------------------------------------------

表反射允许 SQLAlchemy 自动从现有数据库模式加载表定义。当使用旧数据库或当您想要避免重复架构定义时，这非常有用。 ``MetaData`` 上的 ``reflect()`` method 读取数据库架构并为找到的所有表创建 ``Table`` objects。您还可以使用 ``autoload_with`` parameter 反映各个表。

.. code-block:: python

    >>> from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
    >>> engine = create_engine("sqlite:///:memory:")
    >>> # 先创建一个表
    >>> with engine.begin() as conn:
    ...     conn.execute(text("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)"))

    >>> # 反映表
    >>> metadata = MetaData()
    >>> metadata.reflect(bind=engine)
    >>> list(metadata.tables.keys())
    ['products']
    >>> products = metadata.tables['products']
    >>> [c.name for c in products.columns]
    ['id', 'name', 'price']

检查数据库架构（Inspect Database Schema）
----------------------------------------------------------------

``inspect()`` function 提供了一种在运行时检查数据库架构详细信息的强大方法。检查员可以检索有关表、列、indexes、国外keys和其他数据库objects的信息。这对于数据库管理任务、模式迁移和 debugging 特别有用。检查器可与 SQLAlchemy 支持的任何数据库配合使用，并在不同的数据库系统之间提供一致的 API。

.. code-block:: python

    >>> from sqlalchemy import create_engine, inspect, MetaData, Table, Column, Integer, String
    >>> engine = create_engine("sqlite:///:memory:")
    >>> metadata = MetaData()
    >>> users = Table("users", metadata,
    ...     Column("id", Integer, primary_key=True),
    ...     Column("name", String(50)))
    >>> metadata.create_all(engine)

    >>> inspector = inspect(engine)
    >>> inspector.get_table_names()
    ['users']
    >>> inspector.get_columns('users')  # doctest: +ELLIPSIS
    [{'name': 'id', ...}, {'name': 'name', ...}]

插入数据（Insert Data）
----------------------------------

``insert()`` 构造为表创建 INSERT statement。您可以使用 ``values()`` method 指定 values 或将它们作为 keyword arguments 传递。对于批量插入，请将 dictionaries 的 list 传递到 ``execute()`` 。如果可能，SQLAlchemy 将生成高效的多行 INSERT statements。 ``returning()`` method 可以在插入后像主 keys 一样检索自动生成的 values。

.. code-block:: python

    >>> from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, insert
    >>> engine = create_engine("sqlite:///:memory:")
    >>> metadata = MetaData()
    >>> users = Table("users", metadata,
    ...     Column("id", Integer, primary_key=True),
    ...     Column("name", String(50)))
    >>> metadata.create_all(engine)

    >>> # 单刀片
    >>> with engine.begin() as conn:
    ...     conn.execute(insert(users).values(name="Alice"))
    ...     # 批量插入
    ...     conn.execute(insert(users), [{"name": "Bob"}, {"name": "Carol"}])

    >>> with engine.connect() as conn:
    ...     result = conn.execute(users.select())
    ...     print(result.fetchall())
    [(1, 'Alice'), (2, 'Bob'), (3, 'Carol')]

选择数据（Select Data）
----------------------------------

``select()`` 构造创建 SELECT statements 和 Pythonic API。您可以指定要检索的列、使用 ``where()`` 添加 WHERE 子句、使用 ``order_by()`` 对结果进行排序以及使用 ``limit()`` 和 ``offset()`` 限制结果。 SQL Expression 语言使用 Python operators，如 ``==`` 、 ``!=`` 、 ``>`` 、 ``<`` ，它们被重载以生成 SQL 条件。这提供了 type 的安全性并防止 SQL 注入。

.. code-block:: python

    >>> from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select, insert
    >>> engine = create_engine("sqlite:///:memory:")
    >>> metadata = MetaData()
    >>> users = Table("users", metadata,
    ...     Column("id", Integer, primary_key=True),
    ...     Column("name", String(50)),
    ...     Column("age", Integer))
    >>> metadata.create_all(engine)

    >>> with engine.begin() as conn:
    ...     conn.execute(insert(users), [
    ...         {"name": "Alice", "age": 30},
    ...         {"name": "Bob", "age": 25},
    ...         {"name": "Carol", "age": 35}])

    >>> with engine.connect() as conn:
    ...     # 选择全部
    ...     result = conn.execute(select(users))
    ...     print(result.fetchall())
    ...     # 有条件选择
    ...     result = conn.execute(select(users).where(users.c.age > 28))
    ...     print(result.fetchall())
    [(1, 'Alice', 30), (2, 'Bob', 25), (3, 'Carol', 35)]
    [(1, 'Alice', 30), (3, 'Carol', 35)]

更新数据（Update Data）
----------------------------------

``update()`` 构造创建 UPDATE statements。使用 ``where()`` 指定要更新哪些行，使用 ``values()`` 指定更新 set 新列 values。如果没有 WHERE 子句，表中的所有行都将被更新。 ``returning()`` method 可以检索更新的 values。对于每行具有不同 values 的批量更新，请使用 ``bindparam()`` 创建参数化 statements。

.. code-block:: python

    >>> from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
    >>> from sqlalchemy import select, insert, update
    >>> engine = create_engine("sqlite:///:memory:")
    >>> metadata = MetaData()
    >>> users = Table("users", metadata,
    ...     Column("id", Integer, primary_key=True),
    ...     Column("name", String(50)))
    >>> metadata.create_all(engine)

    >>> with engine.begin() as conn:
    ...     conn.execute(insert(users), [{"name": "Alice"}, {"name": "Bob"}])
    ...     conn.execute(update(users).where(users.c.name == "Alice").values(name="Alicia"))

    >>> with engine.connect() as conn:
    ...     result = conn.execute(select(users))
    ...     print(result.fetchall())
    [(1, 'Alicia'), (2, 'Bob')]

删除数据（Delete Data）
----------------------------------

``delete()`` 构造创建 DELETE statements。始终使用 ``where()`` 指定要删除的行，除非您打算删除所有行。与其他 DML statements 一样， ``delete()`` 支持 ``returning()`` 检索已删除的行。请小心 DELETE statements，因为它们会从数据库中永久删除数据。

.. code-block:: python

    >>> from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
    >>> from sqlalchemy import select, insert, delete
    >>> engine = create_engine("sqlite:///:memory:")
    >>> metadata = MetaData()
    >>> users = Table("users", metadata,
    ...     Column("id", Integer, primary_key=True),
    ...     Column("name", String(50)))
    >>> metadata.create_all(engine)

    >>> with engine.begin() as conn:
    ...     conn.execute(insert(users), [{"name": "Alice"}, {"name": "Bob"}, {"name": "Carol"}])
    ...     conn.execute(delete(users).where(users.c.name == "Bob"))

    >>> with engine.connect() as conn:
    ...     result = conn.execute(select(users))
    ...     print(result.fetchall())
    [(1, 'Alice'), (3, 'Carol')]

SQL 表达式语言（SQL Expression Language）
--------------------------------------------------------------------

SQLAlchemy的SQL Expression语言提供了Pythonic的方式来构造SQL statements。列objects支持比较operators（ ``==`` 、 ``!=`` 、 ``>`` 、 ``<`` ），逻辑operators（ ``&`` 为AND， ``|`` 为OR）和 methods，如 ``in_()`` 、 ``like()`` 、 ``between()`` 和 ``is_()`` 。这些 expressions 是可组合的，可以组合起来构建 complex 查询，同时保持可读性和 type 安全性。

.. code-block:: python

    >>> from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
    >>> from sqlalchemy import select, insert, and_, or_
    >>> engine = create_engine("sqlite:///:memory:")
    >>> metadata = MetaData()
    >>> users = Table("users", metadata,
    ...     Column("id", Integer, primary_key=True),
    ...     Column("name", String(50)),
    ...     Column("age", Integer))
    >>> metadata.create_all(engine)

    >>> with engine.begin() as conn:
    ...     conn.execute(insert(users), [
    ...         {"name": "Alice", "age": 30},
    ...         {"name": "Bob", "age": 25},
    ...         {"name": "Carol", "age": 35}])

    >>> with engine.connect() as conn:
    ...     # AND 状况
    ...     stmt = select(users).where(and_(users.c.age > 25, users.c.age < 35))
    ...     print(conn.execute(stmt).fetchall())
    ...     # OR 状况
    ...     stmt = select(users).where(or_(users.c.name == "Alice", users.c.name == "Bob"))
    ...     print(conn.execute(stmt).fetchall())
    ...     # IN条款
    ...     stmt = select(users).where(users.c.name.in_(["Alice", "Carol"]))
    ...     print(conn.execute(stmt).fetchall())
    [(1, 'Alice', 30)]
    [(1, 'Alice', 30), (2, 'Bob', 25)]
    [(1, 'Alice', 30), (3, 'Carol', 35)]

连接表（Join Tables）
--------------------------------

``join()`` method 在表之间创建 JOIN 子句。 SQLAlchemy 可以根据外部 key 关系自动确定联接条件，也可以显式指定它们。使用 ``select_from()`` 指定 SELECT statement 中的联接表。 SQLAlchemy 支持 INNER JOIN（默认）、LEFT OUTER JOIN、RIGHT OUTER JOIN 和 FULL OUTER、JOIN 至 ``isouter`` 和 ``full`` 、parameters。

.. code-block:: python

    >>> from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
    >>> from sqlalchemy import select, insert
    >>> engine = create_engine("sqlite:///:memory:")
    >>> metadata = MetaData()
    >>> users = Table("users", metadata,
    ...     Column("id", Integer, primary_key=True),
    ...     Column("name", String(50)))
    >>> orders = Table("orders", metadata,
    ...     Column("id", Integer, primary_key=True),
    ...     Column("user_id", Integer, ForeignKey("users.id")),
    ...     Column("product", String(50)))
    >>> metadata.create_all(engine)

    >>> with engine.begin() as conn:
    ...     conn.execute(insert(users), [{"name": "Alice"}, {"name": "Bob"}])
    ...     conn.execute(insert(orders), [
    ...         {"user_id": 1, "product": "Book"},
    ...         {"user_id": 1, "product": "Pen"},
    ...         {"user_id": 2, "product": "Laptop"}])

    >>> with engine.connect() as conn:
    ...     stmt = select(users.c.name, orders.c.product).select_from(
    ...         users.join(orders))
    ...     print(conn.execute(stmt).fetchall())
    [('Alice', 'Book'), ('Alice', 'Pen'), ('Bob', 'Laptop')]

聚合函数（Aggregate Functions）
--------------------------------------------------

SQLAlchemy 为 SQL 聚合提供 functions，例如 ``sqlalchemy.func`` namespace 中的 ``count()`` 、 ``sum()`` 、 ``avg()`` 、 ``min()`` 和 ``max()`` 。这些可以在 SELECT statements 中使用，并与 ``group_by()`` 组合进行分组聚合。 ``func`` object 是一个特殊的 namespace，它为您在其上访问的任何 function 名称生成 SQL function 调用。

.. code-block:: python

    >>> from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
    >>> from sqlalchemy import select, insert, func
    >>> engine = create_engine("sqlite:///:memory:")
    >>> metadata = MetaData()
    >>> sales = Table("sales", metadata,
    ...     Column("id", Integer, primary_key=True),
    ...     Column("product", String(50)),
    ...     Column("amount", Integer))
    >>> metadata.create_all(engine)

    >>> with engine.begin() as conn:
    ...     conn.execute(insert(sales), [
    ...         {"product": "A", "amount": 100},
    ...         {"product": "A", "amount": 150},
    ...         {"product": "B", "amount": 200}])

    >>> with engine.connect() as conn:
    ...     # 计算所有行数
    ...     result = conn.execute(select(func.count()).select_from(sales))
    ...     print(result.scalar())
    ...     # 与分组求和
    ...     stmt = select(sales.c.product, func.sum(sales.c.amount)).group_by(sales.c.product)
    ...     print(conn.execute(stmt).fetchall())
    3
    [('A', 250), ('B', 200)]

删除表（Drop Tables）
--------------------------------

可以使用 ``Table`` object 上的 ``drop()`` method 或 ``MetaData`` 上的 ``drop_all()`` 来删除所有表。如果表不存在， ``checkfirst`` parameter 可防止出现错误。在生产中小心这些操作，因为它们会永久删除数据和架构。在删除表之前始终备份数据库。

.. code-block:: python

    >>> from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, inspect
    >>> engine = create_engine("sqlite:///:memory:")
    >>> metadata = MetaData()
    >>> users = Table("users", metadata, Column("id", Integer, primary_key=True))
    >>> products = Table("products", metadata, Column("id", Integer, primary_key=True))
    >>> metadata.create_all(engine)

    >>> inspector = inspect(engine)
    >>> sorted(inspector.get_table_names())
    ['products', 'users']

    >>> # 删除单表
    >>> users.drop(engine)
    >>> sorted(inspect(engine).get_table_names())
    ['products']

    >>> # 删除所有表
    >>> metadata.drop_all(engine)
    >>> inspect(engine).get_table_names()
    []
