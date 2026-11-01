"""保留英文版锚点，为中文网站生成目录及发布元数据。"""
import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree.ElementTree import Element, SubElement, ElementTree

from docutils import nodes
from sphinx.errors import ExtensionError


def restore_anchors(app, doctree):
    """按原章节顺序保留 ID，同时保留中文版自动生成的 ID。"""
    name = app.env.docname
    legacy = app._cn_legacy['documents'].get(name)
    if not legacy:
        return
    sections = list(doctree.findall(nodes.section))
    if len(sections) != len(legacy['sections']):
        raise ExtensionError(f'{name}: 章节数量与英文基线不一致，请更新兼容清单')
    by_tag = defaultdict(list)
    for node in doctree.findall(nodes.Element):
        by_tag[node.tagname].append(node)
    for record in legacy['nodes']:
        candidates = by_tag[record['tag']]
        if record['ordinal'] >= len(candidates):
            continue
        node = candidates[record['ordinal']]
        for anchor in reversed(record['ids']):
            if anchor in legacy['ids'] or anchor not in doctree.ids or doctree.ids[anchor] is node:
                previous = doctree.ids.get(anchor)
                if previous is not None and previous is not node and anchor in previous['ids']:
                    previous['ids'].remove(anchor)
                if anchor in node['ids']:
                    node['ids'].remove(anchor)
                node['ids'].insert(0, anchor)
                doctree.ids[anchor] = node
    # 恢复 autosectionlabel 的英文引用名，显示文字则使用双语标题。
    titles = {anchor: section[0].astext()
              for section in sections for anchor in section['ids']}
    domain = app.env.domaindata['std']
    for label, (docname, anchor, old_title) in app._cn_legacy['labels'].items():
        if docname == name:
            domain['labels'][label] = (name, anchor, titles.get(anchor, old_title))
            domain['anonlabels'][label] = (name, anchor)


def load_legacy(app):
    app._cn_legacy = json.loads((Path(app.srcdir) / 'legacy-anchors.json').read_text())


def page_context(app, pagename, templatename, context, doctree):
    context['cn_page_sections'] = []
    if doctree is not None:
        for section in doctree.findall(nodes.section):
            depth = 0
            parent = section.parent
            while parent is not None:
                depth += isinstance(parent, nodes.section)
                parent = parent.parent
            context['cn_page_sections'].append({
                'id': section['ids'][0], 'title': section[0].astext(), 'depth': depth,
            })
    context['site_baseurl'] = app.config.html_baseurl.rstrip('/') + '/'
    context['site_pageurl'] = (context['site_baseurl'] +
                               app.builder.get_target_uri(pagename))


def write_metadata(app, exception):
    if exception or app.builder.format != 'html':
        return
    out = Path(app.outdir)
    base = app.config.html_baseurl.rstrip('/') + '/'
    path = urlsplit(base).path
    urls = Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for name in sorted(app.env.found_docs):
        if name == '404':
            continue
        SubElement(SubElement(urls, 'url'), 'loc').text = base + app.builder.get_target_uri(name)
    ElementTree(urls).write(out / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (out / 'robots.txt').write_text(
        f'User-agent: *\nDisallow: {path}_sources/\n'
        f'Disallow: {path}search.html\nDisallow: {path}genindex.html\n'
        f'Disallow: {path}404.html\nAllow: {path}\nSitemap: {base}sitemap.xml\n')
    commit = os.environ.get('GITHUB_SHA') or subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=app.srcdir, text=True).strip()
    (out / 'version.json').write_text(json.dumps({
        'commit': commit, 'branch': 'lang/cn', 'language': 'zh-CN',
        'source': 'https://github.com/Alex-Shan/pysheeet',
        'upstream': 'https://github.com/crazyguitar/pysheeet',
    }, ensure_ascii=False, indent=2) + '\n')
    (out / '.nojekyll').touch()


def setup(app):
    app.connect('builder-inited', load_legacy)
    app.connect('doctree-read', restore_anchors, priority=900)
    app.connect('html-page-context', page_context)
    app.connect('build-finished', write_metadata)
    return {'version': '1.0', 'parallel_read_safe': False, 'parallel_write_safe': True}
