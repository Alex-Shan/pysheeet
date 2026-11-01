/* 目录只滚动自身，不调用会移动正文的 scrollIntoView。 */
(() => {
    const localize = () => {
      const labels = {
        'Copy to clipboard': '复制到剪贴板', 'Copy': '复制', 'Copied!': '已复制！',
        'Download this page': '下载本页', 'Fullscreen mode': '全屏模式',
        'Source repositories': '源码仓库', 'Toggle primary sidebar': '展开或收起站点导航',
        'Search this book...': '搜索本站…', 'Search the docs ...': '搜索文档…',
        'Search': '搜索', 'Previous page': '上一页', 'Next page': '下一页',
        'Link to this heading': '链接到此标题', 'Main': '站点导航', 'Page': '本页',
        'Search...': '搜索…', 'System Settings': '系统设置', 'Color mode': '配色模式',
        '列印成 PDF': '打印为 PDF', 'Back to top': '返回顶部', 'Open/close menu': '展开或收起菜单',
        'Show source': '查看源码', 'Toggle navigation': '展开或收起导航',
      };
      document.querySelectorAll('[aria-label], [title], [placeholder], [data-tooltip]').forEach(el => {
        ['aria-label', 'title', 'placeholder', 'data-tooltip'].forEach(attr => {
          const value = el.getAttribute(attr);
          if (labels[value]) el.setAttribute(attr, labels[value]);
        });
      });
    };

  const init = () => {
    localize();
    new MutationObserver(localize).observe(document.body, { childList: true, subtree: true });
    const toc = document.querySelector('#cn-page-toc');
    if (!toc) return;
    const details = toc.querySelector('details');
    const scroller = toc.querySelector('nav');
    const links = Array.from(scroller.querySelectorAll('a'));
    const sections = links.map(link => document.getElementById(decodeURIComponent(link.hash.slice(1))));
    const wide = window.matchMedia('(min-width: 1200px)');
    let active = -1;
    let scheduled = false;
    const reveal = () => {
      if (active < 0 || !details.open) return;
      const link = links[active];
      const box = scroller.getBoundingClientRect();
      const item = link.getBoundingClientRect();
      if (item.top < box.top + 8) scroller.scrollTop += item.top - box.top - 8;
      else if (item.bottom > box.bottom - 8) scroller.scrollTop += item.bottom - box.bottom + 8;
    };
    const update = () => {
      scheduled = false;
      let current = 0;
      const offset = sections[0] ? parseFloat(getComputedStyle(sections[0]).scrollMarginTop) + (parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0) + 16 : 100;
      sections.forEach((section, index) => {
        if (section && section.getBoundingClientRect().top <= offset) current = index;
      });
      // 最后一节较短时，到达页底也应高亮它。
      if (window.scrollY > 0 && window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) current = links.length - 1;
      if (current !== active) {
        if (active >= 0) links[active].removeAttribute('aria-current');
        active = current;
        links[active].setAttribute('aria-current', 'location');
        reveal();
      }
    };
    const schedule = () => {
      if (!scheduled) { scheduled = true; requestAnimationFrame(update); }
    };
    const layout = () => { details.open = wide.matches; schedule(); };
    layout();
    wide.addEventListener('change', layout);
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);
    window.addEventListener('hashchange', schedule);
    window.addEventListener('pageshow', schedule);
    window.addEventListener('load', schedule);
    if (document.fonts) document.fonts.ready.then(schedule);
    const toggle = document.querySelector('.cn-toc-toggle');
    if (toggle) toggle.addEventListener('click', () => { details.open = !details.open; });
    details.addEventListener('toggle', () => {
      if (toggle) toggle.setAttribute('aria-expanded', String(details.open));
      reveal();
    });
    links.forEach(link => link.addEventListener('click', () => {
      if (!wide.matches) details.open = false;
    }));
    update();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
