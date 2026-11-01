
.. raw:: html

    <h1 align="center">
    <br>
      <a href="https://alex-shan.github.io/pysheeet/"><img src="docs/_static/logo.png" alt="pysheeet" width="200"></a>
    </h1>
    <p align="center">
      <a href="https://github.com/Alex-Shan/pysheeet/actions/workflows/pages.yml">
        <img src="https://github.com/Alex-Shan/pysheeet/actions/workflows/pages.yml/badge.svg?branch=lang%2Fcn" alt="中文文档构建状态">
      </a>
      <a href="https://coveralls.io/github/crazyguitar/pysheeet?branch=master">
        <img src="https://coveralls.io/repos/github/crazyguitar/pysheeet/badge.svg?branch=master" alt="上游覆盖率">
      </a>
      <a href="https://raw.githubusercontent.com/crazyguitar/pysheeet/master/LICENSE">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT 许可证">
      </a>
      <a href="https://doi.org/10.5281/zenodo.15529042">
        <img src="https://zenodo.org/badge/52760178.svg" alt="DOI">
      </a>
    </p>

.. _introduction:

介绍（Introduction）
================================

该项目旨在汇集有用的 Python 代码片段，使编码更快、更容易、更愉快。可以在 `中文网站 <https://alex-shan.github.io/pysheeet/>`_ 查阅全部速查表。原作来自 `crazyguitar/pysheeet <https://github.com/crazyguitar/pysheeet>`_，上游英文网站为 `Pysheeet <https://www.pythonsheets.com/>`_。始终欢迎贡献——随时分叉存储库并提交拉取请求以帮助其成长！

.. _plugin:

插件（Plugin）
====================

**pysheeet** 可用作 Claude Code 插件。安装后，Claude 会自动使用速查表来回答 Python 问题 - 只需自然地提问，技能就会根据上下文触发。

.. _installation:

安装（Installation）
--------------------------------

**作为Claude Code插件（推荐）：**

.. code-block:: bash

    # 第 1 步：添加市场
    claude plugin marketplace add crazyguitar/pysheeet

    # 第 2 步：安装插件
    claude plugin install pysheeet@pysheeet

**本地测试（仅限单会话）：**

.. code-block:: bash

    claude --plugin-dir /path/to/pysheeet

**手动安装（需要克隆存储库）：**

.. code-block:: bash

    git clone https://github.com/crazyguitar/pysheeet.git
    mkdir -p ~/.claude/skills
    cp -r pysheeet/skills/py ~/.claude/skills/py

.. _python-interview-cheatsheet:

Python 面试速查表（Python Interview Cheatsheet）
==================================================================================

按主题索引的精选 Python 面试问题 - 每个问题都直接链接到速查表中回答该问题的部分。使用它在面试前快速查看，或深入了解特定区域（GIL、asyncio、decorators、MRO 等）。

- `Python 面试速查表（Python Interview Cheatsheet） <docs/notes/interview/index.rst>`_

.. _what-s-new-in-python-3:

Python 3 的新增功能（What's New In Python 3）
============================================================================

本部分仅快速浏览 Python 3 中的一些重要功能。如果您对所有最重要的功能感兴趣，请阅读官方文档 `What’s New in Python <https://docs.python.org/3/whatsnew/index.html>`_ 。

- `Python3 中的新功能（New in Python3） <docs/notes/python-new-py3.rst>`_


.. _cheat-sheet:

速查表（Cheat Sheet）
================================

核心 Python 基础知识包括 data types、functions、classes 以及日常编程任务的常用模式。

- `从头开始（From Scratch） <docs/notes/basic/python-basic.rst>`_
- `未来特性（Future） <docs/notes/basic/python-future.rst>`_
- `类型标注（Typing） <docs/notes/basic/python-typing.rst>`_
- `类（Class） <docs/notes/basic/python-object.rst>`_
- `函数（Function） <docs/notes/basic/python-func.rst>`_
- `Unicode 字符（Unicode） <docs/notes/basic/python-unicode.rst>`_
- `列表（List） <docs/notes/basic/python-list.rst>`_
- `集合（Set） <docs/notes/basic/python-set.rst>`_
- `字典（Dictionary） <docs/notes/basic/python-dict.rst>`_
- `堆（Heap） <docs/notes/basic/python-heap.rst>`_
- `生成器（Generator） <docs/notes/basic/python-generator.rst>`_
- `Regular expression <docs/notes/basic/python-rexp.rst>`_


.. _system:

系统（System）
====================

日期/时间处理、文件 I/O 和操作系统接口。

- `日期时间（Datetime） <docs/notes/os/python-date.rst>`_ - 时间戳、格式化、解析、时区、时间增量
- `文件和 I/O（Files and I/O） <docs/notes/os/python-io.rst>`_ - 读取、写入、pathlib、shutil、临时文件
- `操作系统（Operating System） <docs/notes/os/python-os.rst>`_ - Processes，环境，系统调用


.. _concurrency:

并发（Concurrency）
==============================

用于并行执行的线程、multiprocessing 和 concurrent.futures。涵盖同步原语、process 池以及绕过 GIL。

- `线程（Threading） <docs/notes/concurrency/python-threading.rst>`_ - Threads、locks、semaphores、事件、条件
- `多进程（Multiprocessing） <docs/notes/concurrency/python-multiprocessing.rst>`_ - Processes、池、共享内存、IPC
- `concurrent.futures 用法（concurrent.futures） <docs/notes/concurrency/python-futures.rst>`_ - 执行者，期货，callbacks


.. _asyncio:

异步编程（Asyncio）
==========================

Asynchronous 与 Python 的 ``asyncio`` module 一起编程。涵盖 coroutines、event loops、任务、网络和高级模式。

- `A Hitchhiker's Guide to Asynchronous Programming <docs/notes/asyncio/python-asyncio-guide.rst>`_ - 设计理念和演变
- `异步基础知识（Asyncio Basics） <docs/notes/asyncio/python-asyncio-basic.rst>`_ - Coroutines，任务，收集，超时
- `异步网络（Asyncio Networking） <docs/notes/asyncio/python-asyncio-server.rst>`_ - TCP/UDP 服务器、HTTP、SSL/TLS
- `Asyncio 进阶（Asyncio Advanced） <docs/notes/asyncio/python-asyncio-advanced.rst>`_ - 同步、queues、子进程


.. _c-c-extensions:

C/C++ 扩展（C/C++ Extensions）
====================================================

针对性能关键型代码的本机扩展。涵盖现代 pybind11（由 PyTorch、TensorFlow 使用）、ctypes、cffi、Cython 和传统的 Python C API。还包括 Python 开发人员学习现代 C++ 语法的指南。

- `ctypes 接口（ctypes） <docs/notes/extension/python-ctypes.rst>`_ - 加载共享的 libraries 而不编译
- `Python C API 用法（Python C API） <docs/notes/extension/python-capi.rst>`_ - 传统 C 扩展参考
- `现代 C/C++ 扩展（Modern C/C++ Extensions） <docs/notes/extension/python-cext-modern.rst>`_ - pybind11、Cython
- `从 Python 学习 C++（Learn C++ from Python） <docs/notes/extension/cpp-from-python.rst>`_ - 适用于 Python 开发人员的现代 C++


.. _security:

安全（Security）
========================

现代加密实践和常见的安全漏洞。涵盖加密、TLS/SSL，以及为什么遗留模式很危险。

- `现代密码学（Modern Cryptography） <docs/notes/security/python-crypto.rst>`_ - AES-GCM、RSA-OAEP、Ed25519、Argon2
- `TLS/SSL及证书（TLS/SSL and Certificates） <docs/notes/security/python-tls.rst>`_ - HTTPS 服务器，证书生成
- `Common Vulnerabilities <docs/notes/security/python-vulnerability.rst>`_ - Padding 预言机、注入、定时攻击


.. _network:

网络（Network）
======================

使用 Python sockets 进行低级网络编程。涵盖 TCP/UDP 通信、服务器实现、asynchronous I/O、SSL/TLS 加密和数据包分析。

- `套接字基础知识（Socket Basics） <docs/notes/network/python-socket.rst>`_
- `套接字服务器（Socket Servers） <docs/notes/network/python-socket-server.rst>`_
- `异步套接字 I/O（Async Socket I/O） <docs/notes/network/python-socket-async.rst>`_
- `SSL/TLS 套接字（SSL/TLS Sockets） <docs/notes/network/python-socket-ssl.rst>`_
- `数据包嗅探（Packet Sniffing） <docs/notes/network/python-socket-sniffer.rst>`_
- `SSH and Tunnels <docs/notes/network/python-ssh.rst>`_


.. _database:

数据库（Database）
==========================

数据库访问用SQLAlchemy，Python最受欢迎的是ORM。涵盖连接管理、原始 SQL、object 关系映射和常见查询模式。

- `SQLAlchemy 基础知识（SQLAlchemy Basics） <docs/notes/database/python-sqlalchemy.rst>`_
- `SQLAlchemy ORM 用法（SQLAlchemy ORM） <docs/notes/database/python-sqlalchemy-orm.rst>`_
- `SQLAlchemy 查询配方（SQLAlchemy Query Recipes） <docs/notes/database/python-sqlalchemy-query.rst>`_


.. _llm:

大语言模型（LLM）
====================

大型语言模型 (LLM) 训练、推理和优化。涵盖用于模型开发的 PyTorch、跨 GPU 的分布式训练以及用于高性能 LLM 推理和服务的 vLLM/SGLang。

- `PyTorch 框架（PyTorch） <docs/notes/llm/pytorch.rst>`_ - Tensors、autograd、神经网络、训练 loops
- `Megatron <docs/notes/llm/megatron.rst>`_ - NVIDIA Megatron 训练/微调框架与 enroot/pyxis
- `LLM 服务（LLM Serving） <docs/notes/llm/llm-serving.rst>`_ - vLLM 和 SGLang 用于使用 TP/PP/DP/EP 进行生产推理
- `LLM 基准测试（LLM Benchmark） <docs/notes/llm/llm-bench.rst>`_ - 用于测量服务性能的 Benchmark 套件


.. _hpc:

高性能计算（HPC）
====================

用于集群管理和作业调度的高性能计算工具。涵盖 Slurm 工作负载管理器和 Ray，用于 GPU 集群上的分布式计算。

- `Slurm 调度（Slurm） <docs/notes/hpc/slurm.rst>`_
- `Ray 集群（Ray Cluster） <docs/notes/hpc/ray.rst>`_


.. _blog:

博客（Blog）
================

补充主题涵盖 Python 内部结构、debugging 技术以及其他地方不适合的语言功能。

- `更多 GPU Ranks 下的 NCCL 多链路广播（NCCL Multi-Rail Broadcast with More GPU Ranks） <docs/notes/appendix/nccl-ring.rst>`_
- `AWS EFA 上的 NVSHMEM Multi-NIC 支持（NVSHMEM Multi-NIC Support with AWS EFA） <docs/notes/appendix/nvshmem-multi-nic.rst>`_
- `分离式 Prefill/Decode 是 LLM 服务的灵丹妙药吗？（Is Disaggregated Prefill/Decode a Silver Bullet for LLM Serving?） <docs/notes/appendix/disaggregated-prefill-decode.rst>`_
- `使用 NCCL GIN 和 Nsys 监控 EFA（Monitoring EFA with NCCL GIN and Nsys） <docs/notes/appendix/megatron-efa-monitoring.rst>`_
- `AWS 上 NCCL 的 GPU 主动发起网络通信（GPU-Initiated Networking for NCCL on AWS） <docs/notes/appendix/nccl-gin.rst>`_
- `PEP 572 and the walrus operator <docs/notes/appendix/python-walrus.rst>`_
- `GNU 调试器中的 Python 解释器（Python Interpreter in GNU Debugger） <docs/notes/appendix/python-gdb.rst>`_

.. _pdf-version:

PDF 版本（PDF Version）
======================================

`pdf`_

.. _pdf: https://media.readthedocs.org/pdf/pysheeet/latest/pysheeet.pdf

.. _how-to-run-the-server:

运行服务器（How to run the server）
========================================================

.. code-block:: bash

    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt
    $ make
    $ python app.py

    # URL: 本地主机:5000

中文文档的构建与维护（Building and Maintaining Chinese Documentation）
=====================================================================

本分支为简体中文版本，保留原作者 crazyguitar 的署名、MIT 许可证和来源。
示例中的 API、标识符、命令、字符串与输出保持原样；自然语言注释使用中文。
位图、性能截图和录屏保留原始数据，中文图例解释其中的说明性标签。
上游 PDF 仍为英文，不由本分支生成。

构建环境（Build Environment）
----------------------------

使用 Python 3.12.14。文档依赖独立于示例运行依赖，直接版本列于
``requirements-docs.in``，全部传递依赖及哈希列于 ``requirements-docs.lock``。
安装 `uv <https://docs.astral.sh/uv/>`_ 后，可执行：

.. code-block:: bash

    uv python install 3.12.14
    uv venv --python 3.12.14 .venv
    . .venv/bin/activate
    uv pip sync --require-hashes requirements-docs.lock
    make docs-check

也可以在已有的 Python 3.12.14 环境中运行：

.. code-block:: bash

    python -m venv .venv
    . .venv/bin/activate
    python -m pip install --require-hashes -r requirements-docs.lock
    make docs-check
    make docs-preview

本地预览地址为 ``http://localhost:8000/``；构建产物位于 ``docs/_build/html``。
部署后的项目根路径为 ``/pysheeet/``，canonical 和 sitemap 指向公开 Pages 地址。

验证与发布（Validation and Deployment）
--------------------------------------

静态检查覆盖全部章节、旧锚点、内部链接、静态资源、Python AST、源码 tokens
及文档示例的非注释内容。``docs/legacy-anchors.json`` 与
``docs/legacy-examples.json`` 记录英文基线，不应随意更新以绕过检查。
纯产品名或 API 名称也配以中文说明，目录文字与实际标题一致。

浏览器检查使用锁定的 Node.js 工具依赖，CI 使用 Node.js 22：

.. code-block:: bash

    npm ci --prefix tools/browser
    cd tools/browser
    npx playwright install chromium
    npm test

使用已安装的 Chrome 时，可以设置 ``CHROME_PATH`` 为可执行文件路径。
检查覆盖 1440、1024、390 和 320 像素宽度、目录上下滚动、正文位置稳定、
旧锚点直达、浏览历史、复制、搜索和语法高亮。验证线上站点时执行：

.. code-block:: bash

    TEST_BASE_URL=https://alex-shan.github.io/pysheeet/ npm test

仅推送 ``lang/cn`` 会触发中文 Pages 发布；Pull Request 只执行验证。
Pages 来源使用 GitHub Actions，``github-pages`` environment 仅允许
``lang/cn`` 部署。``version.json`` 包含产物的来源 commit，可与 Actions
部署记录核对。默认分支和示例依赖不因文档发布而改变。

详细验证范围与运行限制见 `中文化验证记录 <VALIDATION.zh-CN.md>`_。
