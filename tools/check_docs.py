"""检查中文站点的链接、旧锚点、目录与示例代码。"""
import argparse
import ast
import hashlib
import io
import json
import pickle
import re
import subprocess
import tokenize
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

from bs4 import BeautifulSoup
from docutils import nodes
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.token import Comment

ROOT = Path(__file__).resolve().parents[1]
BASE = '99dfbfff7c4bde7e43c9b9b5244da078e13b9158'


def code_fingerprint(text, language=None, filename=None):
    try:
        lexer = get_lexer_for_filename(filename) if filename else get_lexer_by_name(language or 'python')
    except Exception:
        return hashlib.sha256(text.encode()).hexdigest()
    # 保留全部非注释字符，包括字符串和输出，只忽略行末空格。
    code = ''.join(value for _, kind, value in lexer.get_tokens_unprocessed(text) if kind not in Comment or kind in Comment.Preproc)
    code = '\n'.join(line.rstrip() for line in code.splitlines())
    return hashlib.sha256(code.encode()).hexdigest()


def snapshot_examples(doctrees):
    result = {}
    for path in sorted(doctrees.rglob('*.doctree')):
        tree = pickle.loads(path.read_bytes())
        result[path.relative_to(doctrees).with_suffix('').as_posix()] = [
            {'language': node.get('language', 'python'),
             'hash': code_fingerprint(node.astext(), node.get('language', 'python'))}
            for node in tree.findall(nodes.literal_block)
        ]
    return result


def source_checks(errors):
    files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE], cwd=ROOT, text=True).splitlines()
    for name in files:
        if Path(name).suffix not in {'.py', '.c', '.cpp', '.h', '.sh'} or name == 'docs/conf.py':
            continue
        before = subprocess.check_output(['git', 'show', f'{BASE}:{name}'], cwd=ROOT).decode()
        after = (ROOT / name).read_text()
        if before == after:
            continue
        if code_fingerprint(before, filename=name) != code_fingerprint(after, filename=name):
            errors.append(f'非注释源码变化: {name}')
        if name.endswith('.py'):
            if ast.dump(ast.parse(before)) != ast.dump(ast.parse(after)):
                errors.append(f'Python AST 变化: {name}')
            def tokens(text):
                return [(t.type, t.string) for t in tokenize.generate_tokens(io.StringIO(text).readline)
                        if t.type not in {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.ENCODING}]
            if tokens(before) != tokens(after):
                errors.append(f'Python token 变化: {name}')


def check(html_dir, doctrees, examples):
    errors = []
    pages = {p.resolve(): BeautifulSoup(p.read_text(), 'html.parser') for p in html_dir.rglob('*.html') if '_static' not in p.relative_to(html_dir).parts}
    all_ids = {p: {n['id'] for n in soup.select('[id]')} for p, soup in pages.items()}
    manifest = json.loads((ROOT / 'docs/legacy-anchors.json').read_text())
    section_count = 0
    for name, legacy in manifest['documents'].items():
        page = (html_dir / (name + '.html')).resolve()
        if page not in pages:
            errors.append(f'缺少页面: {name}')
            continue
        soup = pages[page]
        ids = all_ids[page]
        missing = set(legacy['ids']) - ids
        if missing:
            errors.append(f'{name}: 缺少旧锚点 {sorted(missing)}')
        sections = soup.select('article section')
        links = soup.select('#cn-toc-scroll a')
        if len(sections) != len(links):
            errors.append(f'{name}: 目录 {len(links)} 与章节 {len(sections)} 数量不同')
        for section, link in zip(sections, links):
            heading = section.find(re.compile('^h[1-6]$'), recursive=False)
            if heading:
                heading = BeautifulSoup(str(heading), 'html.parser')
                for permalink in heading.select('.headerlink'): permalink.decompose()
                title = heading.get_text().strip()
                if link.get_text().strip() != title:
                    errors.append(f'{name}: 目录标题不一致 {title}')
                if not re.search(r'[\u4e00-\u9fff].*（.+）$', title):
                    # 纯产品/API 名称也使用一个中文说明，避免遗漏整节。
                    errors.append(f'{name}: 标题未双语化 {title}')
            section_count += 1
        duplicates = [n['id'] for n in soup.select('[id]')]
        if len(duplicates) != len(set(duplicates)):
            errors.append(f'{name}: 重复 HTML ID')
        if soup.html.get('lang') != 'zh-CN':
            errors.append(f'{name}: HTML lang 不是 zh-CN')
    base = 'https://alex-shan.github.io/pysheeet/'
    for page, soup in pages.items():
        relative = page.relative_to(html_dir.resolve()).as_posix()
        for node in soup.select('[href], [src]'):
            value = node.get('href') or node.get('src')
            parsed = urlsplit(value)
            if parsed.scheme in {'mailto', 'javascript', 'data', 'tel'}:
                continue
            target = urlsplit(urljoin(base + relative, value))
            if target.netloc != urlsplit(base).netloc:
                continue
            if not target.path.startswith('/pysheeet/'):
                errors.append(f'{relative}: 本站链接缺少项目路径 {value}')
                continue
            dest = (html_dir / unquote(target.path[len('/pysheeet/'):])).resolve()
            if dest.is_dir():
                dest /= 'index.html'
            if not dest.is_file():
                errors.append(f'{relative}: 链接或资源不存在 {value}')
            elif target.fragment and dest in all_ids and unquote(target.fragment) not in all_ids[dest]:
                errors.append(f'{relative}: 目标锚点不存在 {value}')
    current = snapshot_examples(doctrees)
    original = json.loads(examples.read_text())
    for name, blocks in original.items():
        actual = current.get(name, [])
        if len(blocks) != len(actual):
            errors.append(f'{name}: 示例数量改变 {len(blocks)} -> {len(actual)}')
        for i, (before, after) in enumerate(zip(blocks, actual), 1):
            if before != after:
                errors.append(f'{name}: 第 {i} 个示例非注释内容改变')
    source_checks(errors)
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'通过：{len(manifest["documents"])} 篇文档、{section_count} 个章节、旧锚点、内部链接、静态资源和示例行为。')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', type=Path, default=ROOT / 'docs/_build/html')
    parser.add_argument('--doctrees', type=Path, default=ROOT / 'docs/_build/doctrees')
    parser.add_argument('--examples', type=Path, default=ROOT / 'docs/legacy-examples.json')
    parser.add_argument('--record-examples', type=Path)
    args = parser.parse_args()
    if args.record_examples:
        args.record_examples.write_text(json.dumps(snapshot_examples(args.doctrees), ensure_ascii=False, indent=2) + '\n')
    else:
        check(args.html, args.doctrees, args.examples)
