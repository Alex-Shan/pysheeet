.. python-cheatsheet documentation master file, created by
   sphinx-quickstart on Sun Feb 28 09:26:04 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. meta::
    :description lang=zh_CN: 全面的 Python 速查表，为 Python 开发人员提供实用的代码片段、示例和教程。了解 Python 基础知识、高级主题、数据库、网络等。
    :keywords: Python, Python Cheat Sheet, Python Tutorial, Python Examples, Python Code Snippets, Programming, Development, Python Reference, Python Guide


Python 速查表 - 带有代码示例的完整指南（Python Cheat Sheet - Complete Guide with Code Examples）
================================================================================================================================================================

欢迎来到 **pysheeet** - 您的终极 Python 速查表！这个综合资源包含实用的 Python 代码片段、示例和教程，使各个级别的 Python 开发人员的编码变得更容易、更高效。从基本的 Python 语法到数据库、网络和多任务处理等高级主题，此速查表可作为您完整的 Python 参考指南。非常适合学习 Python 基础知识的初学者和寻求快速代码示例的经验丰富的开发人员。无论您学习 Python 是为了 Web 开发、数据科学、自动化还是一般编程，您都会找到可以节省时间并提高编码效率的实用示例。

始终欢迎贡献——随时分享新片段、改进或更清晰解释的想法！如果您愿意贡献， `fork pysheeet on GitHub`_ 。如果有任何问题或建议，请在 `GitHub Issues`_ 上创建问题。

.. _fork pysheeet on GitHub: https://github.com/crazyguitar/pysheeet
.. _GitHub Issues: https://github.com/crazyguitar/pysheeet/issues

插件（Plugin）
--------------------

**pysheeet** 可用作 `Claude Code <https://claude.com/claude-code>`_ 插件。安装后，Claude 会自动使用速查表来回答 Python 问题。

.. code-block:: bash

    # 第 1 步：添加市场
    claude plugin marketplace add crazyguitar/pysheeet

    # 第 2 步：安装插件
    claude plugin install pysheeet@pysheeet

本地测试和手动安装请参见主要的 `README <https://github.com/Alex-Shan/pysheeet/blob/lang/cn/README.rst>`_ 。

Python 3 的新增功能（What's New In Python 3）
----------------------------------------------------------------------------

官方文档 `What's New In Python`_ 显示了所有最重要的更改。但是，如果您太忙而无法阅读全部更改，本部分将简要介绍 Python 3 中的新功能。

.. _What's New In Python: https://docs.python.org/3/whatsnew/index.html

.. toctree::
   :maxdepth: 1

   notes/python-new-py3

博客（Blog）
----------------

该网站还涵盖与 LLM 训练、推理、HPC 网络、分布式系统、GPU 计算和 :doc:`blog </notes/appendix/index>` 中的 Python debugging 技术相关的高级主题。

Python 速查表（Python Cheat Sheet）
------------------------------------------------------------

本节重点介绍常用的 Python 代码片段。该速查表不仅涵盖了 Python 的核心功能，还涵盖了基本的数据结构、算法和常用的 modules，以帮助程序员高效地处理日常任务。

.. toctree::
   :maxdepth: 1

   notes/interview/index
   notes/basic/index
   notes/os/index
   notes/concurrency/index
   notes/asyncio/index
   notes/network/index
   notes/database/index
   notes/security/index
   notes/extension/index
   notes/llm/index
   notes/hpc/index
