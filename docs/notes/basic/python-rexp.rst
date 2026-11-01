.. meta::
    :description lang=zh_CN: Python regex 速查表涵盖 module、模式匹配、组、前向、后向、替换和常见的 regex 模式以及代码示例
    :keywords: Python, Python3, Python regex, Python regex cheat sheet, regular expression, re module, pattern matching, findall, search, match, sub, lookahead, lookbehind, named groups

==================================================
正则表达式（Regular Expression）
==================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

Regular expressions (regex) 是用于模式匹配和文本操作的强大工具。 Python的 ``re`` module为regex操作提供全面支持。该速查表涵盖了基本匹配、组、环视 assertions、替换以及用于验证电子邮件、URLs、IP 地址等的常见模式。

基本操作（Basic Operations）
--------------------------------------------

``re`` module 提供了多个 functions 用于模式匹配。使用 ``search()`` 查找 string 中任意位置的第一个匹配项，使用 ``match()`` 在开头匹配，使用 ``fullmatch()`` 匹配整个 string。

.. code-block:: python

    >>> import re
    >>> # 搜索 - 查找 string 中的任何位置
    >>> re.search(r'\d+', 'abc123def')
    <re.Match object; span=(3, 6), match='123'>

    >>> # match - 仅在开头匹配
    >>> re.match(r'\d+', '123abc')
    <re.Match object; span=(0, 3), match='123'>
    >>> re.match(r'\d+', 'abc123') is None
    True

    >>> # fullmatch - 匹配整个 string
    >>> re.fullmatch(r'\d+', '123')
    <re.Match object; span=(0, 3), match='123'>
    >>> re.fullmatch(r'\d+', '123abc') is None
    True

``re.findall()`` - 查找所有匹配项（ ``re.findall()`` - Find All Matches）
--------------------------------------------------------------------------------------------------------------------------------

``findall()`` function 将所有非重叠匹配项返回为 strings 的 list。如果模式有组，则返回 tuples 的 list。

.. code-block:: python

    >>> # 找到所有单词
    >>> source = "Hello World Ker HAHA"
    >>> re.findall(r'[\w]+', source)
    ['Hello', 'World', 'Ker', 'HAHA']

    >>> # 找到所有数字
    >>> re.findall(r'\d+', 'a1b22c333')
    ['1', '22', '333']

    >>> # 与组 - 返回 tuples
    >>> re.findall(r'(\w+)=(\d+)', 'a=1 b=2 c=3')
    [('a', '1'), ('b', '2'), ('c', '3')]

``re.split()`` - 按模式分割（ ``re.split()`` - Split by Pattern）
--------------------------------------------------------------------------------------------------------------------

``split()`` function 按模式出现次数拆分 string。使用 ``maxsplit`` 限制分割数。

.. code-block:: python

    >>> re.split(r'\s+', 'a  b   c')
    ['a', 'b', 'c']

    >>> re.split(r'[,;]', 'a,b;c,d')
    ['a', 'b', 'c', 'd']

    >>> re.split(r'(\s+)', 'a b c')  # 保留分隔符
    ['a', ' ', 'b', ' ', 'c']

    >>> re.split(r'\s+', 'a b c d', maxsplit=2)
    ['a', 'b', 'c d']

分组匹配（Group Matching）
----------------------------------------

括号 ``(...)`` 创建捕获组。使用 ``group()`` 访问匹配组。第 0 组是整场比赛，第 1 组是第一个括号内的组，依此类推。

.. code-block:: python

    >>> m = re.search(r'(\d{4})-(\d{2})-(\d{2})', '2016-01-01')
    >>> m.groups()
    ('2016', '01', '01')
    >>> m.group()      # 整场比赛
    '2016-01-01'
    >>> m.group(1)     # 第一组
    '2016'
    >>> m.group(2, 3)  # 多个组
    ('01', '01')

    # 嵌套组 - 通过左括号从左到右编号
    >>> m = re.search(r'(((\d{4})-\d{2})-\d{2})', '2016-01-01')
    >>> m.groups()
    ('2016-01-01', '2016-01', '2016')

非捕获组 ``(?:...)`` （Non-Capturing Group ``(?:...)`` ）
------------------------------------------------------------------------------------------------------

当您需要对交替或量词进行分组但不需要捕获匹配时，请使用 ``(?:...)`` 。这可以提高性能并保持组编号干净。

.. code-block:: python

    >>> url = 'http://stackoverflow.com/'
    >>> # 协议的非捕获组
    >>> m = re.search(r'(?:http|ftp)://([^/\r\n]+)(/[^\r\n]*)?', url)
    >>> m.groups()
    ('stackoverflow.com', '/')

    >>> # 捕获组 - 捕获协议
    >>> m = re.search(r'(http|ftp)://([^/\r\n]+)(/[^\r\n]*)?', url)
    >>> m.groups()
    ('http', 'stackoverflow.com', '/')

命名组 ``(?P<name>...)`` （Named Groups ``(?P<name>...)`` ）
--------------------------------------------------------------------------------------------------------------

命名组使模式更具可读性，并允许通过名称而不是数字进行访问。使用 ``(?P<name>...)`` 定义并使用 ``(?P=name)`` 进行反向引用。

.. code-block:: python

    >>> pattern = r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
    >>> m = re.search(pattern, '2016-01-01')
    >>> m.group('year')
    '2016'
    >>> m.group('month')
    '01'
    >>> m.groupdict()
    {'year': '2016', 'month': '01', 'day': '01'}

    # 命名反向引用
    >>> re.search(r'^(?P<char>[a-z])(?P=char)', 'aa')
    <re.Match object; span=(0, 2), match='aa'>
    >>> re.search(r'^(?P<char>[a-z])(?P=char)', 'ab') is None
    True

反向引用 ``\1`` 、 ``\2`` （Back Reference ``\1`` , ``\2`` ）
------------------------------------------------------------------------------------------------------------

向后引用与前一个捕获组匹配相同的文本。第一组使用 ``\1`` ，第二组使用 ``\2`` ，依此类推。

.. code-block:: python

    >>> # 匹配重复的字符
    >>> re.search(r'([a-z])\1', 'aa') is not None
    True
    >>> re.search(r'([a-z])\1', 'ab') is not None
    False

    >>> # 将 HTML 标签与匹配的关闭标签相匹配
    >>> pattern = r'<([^>]+)>[\s\S]*?</\1>'
    >>> re.search(pattern, '<bold>test</bold>') is not None
    True
    >>> re.search(pattern, '<bold>test</h1>') is not None
    False

替换为 ``re.sub()`` （Substitute with ``re.sub()`` ）
------------------------------------------------------------------------------------------------

``sub()`` function 用替代品 string 替换模式匹配。在替换中使用 ``\1`` 、 ``\2`` 来引用捕获的组。

.. code-block:: python

    >>> # 基本替代
    >>> re.sub(r'[a-z]', ' ', '1a2b3c')
    '1 2 3 '

    >>> # 用组参考替换
    >>> re.sub(r'(\d{4})-(\d{2})-(\d{2})', r'\2/\3/\1', '2016-01-01')
    '01/01/2016'

    >>> # 使用function作为替代品
    >>> re.sub(r'\d+', lambda m: str(int(m.group()) * 2), 'a1b2c3')
    'a2b4c6'

    >>> # 驼峰式格式为 snake_case
    >>> def to_snake(s):
    ...     s = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', s)
    ...     return re.sub(r'([a-z])([A-Z])', r'\1_\2', s).lower()
    ...
    >>> to_snake('CamelCase')
    'camel_case'
    >>> to_snake('SimpleHTTPServer')
    'simple_http_server'

前瞻与后顾断言（Lookahead and Lookbehind）
------------------------------------------------------------------

Lookaround assertions 匹配位置而不消耗字符。它们对于根据上下文匹配模式很有用。

.. list-table::
   :header-rows: 1

   * - 符号
     - 名称
     - 描述
   * - ``(?=...)``
     - 正向前瞻
     - 后方匹配 ...
   * - ``(?!...)``
     - 负向前瞻
     - 后方不匹配 ...
   * - ``(?<=...)``
     - 正向后顾
     - 前方匹配 ...
   * - ``(?<!...)``
     - 负向后顾
     - 前方不匹配 ...


.. code-block:: python

    >>> # 正向前视 - 查找 @ 之前的单词
    >>> re.findall(r'\w+(?=@)', 'user@example.com')
    ['user']

    >>> # 负向先行 - 查找后面没有 px 的数字
    >>> re.findall(r'\d+(?!px)', '12px 34em 56')
    ['1', '34', '56']

    >>> # 正向后查找 - 查找 $ 之后的数字
    >>> re.findall(r'(?<=\$)\d+', '$100 $200')
    ['100', '200']

    >>> # 负向后查找 - 查找不在 $ 之后的数字
    >>> re.findall(r'(?<!\$)\d+', '$100 200')
    ['00', '200']

    >>> # 在从右数 3 位数字组成的组之前插入空格
    >>> re.sub(r'(?=(\d{3})+$)', ' ', '12345678')
    ' 12 345 678'

编译模式以供重用（Compile Pattern for Reuse）
----------------------------------------------------------------------

使用 ``re.compile()`` 创建可重复使用的图案 object。当多次使用相同模式时，这可以提高性能。

.. code-block:: python

    >>> pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    >>> pattern.search('Date: 2024-01-15')
    <re.Match object; span=(6, 16), match='2024-01-15'>
    >>> pattern.findall('2024-01-15 and 2024-02-20')
    ['2024-01-15', '2024-02-20']

正则表达式标志（Regex Flags）
----------------------------------------

标志修改模式行为。常见标志包括 ``re.IGNORECASE`` ( ``re.I`` )、 ``re.MULTILINE`` ( ``re.M`` )、 ``re.DOTALL`` ( ``re.S`` ) 和 ``re.VERBOSE`` ( ``re.X`` )。

.. code-block:: python

    >>> # 不区分大小写
    >>> re.findall(r'[a-z]+', 'Hello World', re.I)
    ['Hello', 'World']

    >>> # 多行 - ^ 和 $ 匹配行边界
    >>> re.findall(r'^\w+', 'line1\nline2', re.M)
    ['line1', 'line2']

    >>> # 多塔尔-.匹配换行符
    >>> re.search(r'a.b', 'a\nb', re.S)
    <re.Match object; span=(0, 3), match='a\nb'>

    >>> # verbose - 允许注释和空格
    >>> pattern = re.compile(r'''
    ...     \d{4}  # year
    ...     -
    ...     \d{2}  # month
    ...     -
    ...     \d{2}  # day
    ... ''', re.X)
    >>> pattern.match('2024-01-15')
    <re.Match object; span=(0, 10), match='2024-01-15'>

比较 HTML 标签（Compare HTML Tags）
----------------------------------------------------------

用于匹配 HTML 标签的不同 types 的通用模式。

.. list-table::
   :header-rows: 1

   * - 标签 Type
     - 图案
     - 例子
   * - 所有标签
     - <[^>]+>
     - <br/>，<a>
   * - 打开标签
     - <[^/>][^>]*>
     - <a>，<表>
   * - 关闭标签
     - </[^>]+>
     - </p>、</a>
   * - 自关闭
     - <[^/>]+/>
     - <br/>


.. code-block:: python

    >>> # 开放标签
    >>> re.search(r'<[^/>][^>]*>', '<table>') is not None
    True
    >>> re.search(r'<[^/>][^>]*>', '</table>') is not None
    False

    >>> # 关闭标签
    >>> re.search(r'</[^>]+>', '</table>') is not None
    True

    >>> # 自闭合标签
    >>> re.search(r'<[^/>]+/>', '<br />') is not None
    True

匹配电子邮件地址（Match Email Address）
----------------------------------------------------------

验证电子邮件地址的模式。请注意，完全符合 RFC 的电子邮件验证极其 complex；这涵盖了常见情况。

.. code-block:: python

    >>> pattern = re.compile(r'^[\w.+-]+@[\w-]+\.[\w.-]+$')
    >>> pattern.match('hello.world@example.com') is not None
    True
    >>> pattern.match('user+tag@sub.domain.org') is not None
    True
    >>> pattern.match('invalid@') is not None
    False

匹配URL（Match URL）
--------------------------------

用于将 URLs 与可选协议、域和路径相匹配的模式。

.. code-block:: python

    >>> pattern = re.compile(r'''
    ...     ^(https?://)?           # optional protocol
    ...     ([\da-z.-]+)            # domain
    ...     \.([a-z.]{2,6})         # TLD
    ...     ([/\w.-]*)*/?$          # path
    ... ''', re.X | re.I)
    >>> pattern.match('https://www.example.com/path') is not None
    True
    >>> pattern.match('example.com') is not None
    True

匹配 IP 地址（Match IP Address）
----------------------------------------------------

用于验证 IPv4 地址（0.0.0.0 到 255.255.255.255）的模式。

.. code-block:: python

    >>> pattern = re.compile(r'''
    ...     ^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}
    ...     (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$
    ... ''', re.X)
    >>> pattern.match('192.168.1.1') is not None
    True
    >>> pattern.match('255.255.255.0') is not None
    True
    >>> pattern.match('256.0.0.0') is not None
    False

匹配 MAC 地址（Match MAC Address）
--------------------------------------------------------

用于验证冒号分隔格式的 MAC 地址的模式。

.. code-block:: python

    >>> pattern = re.compile(r'^([0-9a-f]{2}:){5}[0-9a-f]{2}$', re.I)
    >>> pattern.match('3c:38:51:05:03:1e') is not None
    True
    >>> pattern.match('AA:BB:CC:DD:EE:FF') is not None
    True

匹配电话号码（Match Phone Number）
----------------------------------------------------

常见电话号码格式的模式。

.. code-block:: python

    >>> # US 电话号码
    >>> pattern = re.compile(r'^(\+1)?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$')
    >>> pattern.match('123-456-7890') is not None
    True
    >>> pattern.match('(123) 456-7890') is not None
    True
    >>> pattern.match('+1 123 456 7890') is not None
    True

匹配密码强度（Match Password Strength）
--------------------------------------------------------------

验证密码的模式，最低要求：至少 8 个字符、1 个大写字母、1 个小写字母、1 个数字和 1 个特殊字符。

.. code-block:: python

    >>> pattern = re.compile(r'''
    ...     ^(?=.*[a-z])        # at least one lowercase
    ...     (?=.*[A-Z])         # at least one uppercase
    ...     (?=.*\d)            # at least one digit
    ...     (?=.*[@$!%*?&])     # at least one special char
    ...     [A-Za-z\d@$!%*?&]{8,}$  # at least 8 chars
    ... ''', re.X)
    >>> pattern.match('Passw0rd!') is not None
    True
    >>> pattern.match('weakpass') is not None
    False

简单词法分析器（Simple Lexer）
------------------------------------------

使用 regex 构建一个简单的算术标记器 expressions。这演示了如何使用命名组和 ``scanner()`` 进行词法分析。

.. code-block:: python

    >>> from collections import namedtuple
    >>> tokens = [
    ...     r'(?P<NUMBER>\d+)',
    ...     r'(?P<PLUS>\+)',
    ...     r'(?P<MINUS>-)',
    ...     r'(?P<TIMES>\*)',
    ...     r'(?P<DIVIDE>/)',
    ...     r'(?P<WS>\s+)'
    ... ]
    >>> lex = re.compile('|'.join(tokens))
    >>> Token = namedtuple('Token', ['type', 'value'])
    >>> def tokenize(text):
    ...     scan = lex.scanner(text)
    ...     return (Token(m.lastgroup, m.group())
    ...             for m in iter(scan.match, None) if m.lastgroup != 'WS')
    ...
    >>> list(tokenize('9 + 5 * 2'))
    [Token(type='NUMBER', value='9'), Token(type='PLUS', value='+'), Token(type='NUMBER', value='5'), Token(type='TIMES', value='*'), Token(type='NUMBER', value='2')]

常见模式参考（Common Patterns Reference）
------------------------------------------------------------------

.. code-block:: python

    # 仅数字
    r'^\d+$'

    # 字母数字
    r'^[a-zA-Z0-9]+$'

    # 用户名（3-16 个字符、字母数字、下划线、连字符）
    r'^[a-zA-Z0-9_-]{3,16}$'

    # 十六进制颜色
    r'^#?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$'

    # 日期（YYYY-MM-DD）
    r'^\d{4}-\d{2}-\d{2}$'

    # 时间（HH：MM：SS）
    r'^\d{2}:\d{2}:\d{2}$'

    # Slug（URL-友好的string）
    r'^[a-z0-9]+(?:-[a-z0-9]+)*$'

    # 删除 HTML 标签
    re.sub(r'<[^>]+>', '', html)

    # 从 URL 中提取域
    re.search(r'https?://([^/]+)', url).group(1)

    # 查找所有主题标签
    re.findall(r'#\w+', text)

    # 查找所有@提及
    re.findall(r'@\w+', text)
