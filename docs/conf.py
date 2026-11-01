# pysheeet 中文文档构建配置；原作者 crazyguitar，始于 2016 年。
from datetime import datetime
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).parent / '_ext'))

extensions = [
    'sphinx.ext.todo', 'sphinx.ext.coverage', 'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel', 'myst_parser', 'sphinx_copybutton',
    'sphinx.ext.graphviz', 'sphinx_design', 'sphinx.ext.extlinks',
    'notfound.extension', 'chinese_site',
]
autosectionlabel_prefix_document = True
# 原文中存在同页重复小节；兼容清单保留它们各自的锚点。
suppress_warnings = ['autosectionlabel.*']
myst_enable_extensions = ['colon_fence', 'attrs_inline', 'attrs_block', 'tasklist', 'substitution']
myst_enable_checkboxes = True
myst_heading_anchors = 6
copybutton_prompt_text = r'^\$ '
copybutton_prompt_is_regexp = True

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = 'pysheeet'
author = 'crazyguitar'
copyright = f'2016-{datetime.now().year}, crazyguitar'
version = release = '0.1.0'
language = 'zh_CN'
html_search_language = 'zh'
pygments_style = 'sphinx'
todo_include_todos = True

# 本地和 CI 使用相同的项目路径；部署工作流可传入 Pages 实际地址。
html_baseurl = os.environ.get('PYSHEEET', 'https://alex-shan.github.io/pysheeet/').rstrip('/') + '/'
notfound_urls_prefix = urlsplit(html_baseurl).path
notfound_context = {
    'title': '找不到页面（Page Not Found）',
    'body': '<h1>找不到页面（Page Not Found）</h1><p>请求的页面不存在，请使用目录或搜索查找内容。</p>',
}
html_theme = 'sphinx_book_theme'
html_theme_options = {
    'repository_url': 'https://github.com/Alex-Shan/pysheeet',
    'repository_branch': 'lang/cn', 'path_to_docs': 'docs',
    'use_repository_button': True, 'toc_title': '目录（Contents）',
    'show_toc_level': 6, 'secondary_sidebar_items': [],
    'extra_footer': '中文化版本 · <a href="https://github.com/crazyguitar/pysheeet">原作与来源：crazyguitar/pysheeet</a>',
}
html_title = 'Python 速查表（Python Cheat Sheet）'
html_logo = '_static/logo.svg'
html_favicon = '_static/favicon.ico'
html_static_path = ['_static']
html_extra_path = ['_extra']
html_css_files = ['style.css']
html_js_files = ['cn-navigation.js']
html_context = {'tracking_id': os.environ.get('TRACKING_ID')}
html_sidebars = {'**': ['navbar-logo.html', 'search-button-field.html', 'sbt-sidebar-nav.html']}
latex_documents = [(master_doc, 'python-cheatsheet.tex', html_title, author, 'manual')]
man_pages = [(master_doc, 'python-cheatsheet', html_title, [author], 1)]
texinfo_documents = [(master_doc, 'python-cheatsheet', html_title, author,
                      'python-cheatsheet', 'Python 示例与说明。', 'Miscellaneous')]
