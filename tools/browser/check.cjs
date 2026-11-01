// 验证本地或已部署页面的目录、布局、搜索和复制功能。
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { chromium } = require('playwright');

(async () => {
  let server;
  let base = process.env.TEST_BASE_URL;
  if (!base) {
    const root = path.resolve(__dirname, '../../docs/_build/html');
    const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.json': 'application/json' };
    server = http.createServer((req, res) => {
      const url = new URL(req.url, 'http://localhost');
      const relative = decodeURIComponent(url.pathname).replace(/^\/pysheeet\//, '');
      let file = path.resolve(root, relative || 'index.html');
      if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
      if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
      if (!fs.existsSync(file)) { file = path.join(root, '404.html'); res.statusCode = 404; }
      res.setHeader('Content-Type', types[path.extname(file)] || 'application/octet-stream');
      fs.createReadStream(file).pipe(res);
    });
    await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
    base = `http://127.0.0.1:${server.address().port}/pysheeet/`;
  }
  const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
  const failures = [];
  try {
    for (const width of [1440, 1024, 390, 320]) {
      const context = await browser.newContext({ viewport: { width, height: 900 }, permissions: ['clipboard-read', 'clipboard-write'] });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      page.on('response', response => { if (response.status() >= 400 && !response.url().endsWith('/missing-page.html')) errors.push(`${response.status()} ${response.url()}`); });
      await page.goto(base + 'notes/basic/python-basic.html', { waitUntil: 'networkidle' });
      const toc = page.locator('#cn-page-toc');
      await toc.waitFor();
      if (width < 1200) {
        const heading = await page.locator('article h1').first().boundingBox();
        const summary = await toc.locator('summary').boundingBox();
        assert(heading.y >= summary.y + summary.height, `${width}px 页面标题被目录遮挡：${heading.y} < ${summary.y + summary.height}`);
      }
      fs.mkdirSync(path.resolve(__dirname, '../../docs/_build/reports'), { recursive: true });
      if (width === 1440 || width === 390) await page.screenshot({ path: path.resolve(__dirname, `../../docs/_build/reports/layout-${width}.png`) });
      const count = await toc.locator('a').count();
      assert(count > 20, '长页面需要完整目录');
      assert.equal(await toc.locator('details').evaluate(el => el.open), width >= 1200);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
      assert(!overflow, `${width}px 页面出现横向溢出`);
      if (width < 1200) {
        await page.locator('.cn-toc-toggle').click();
        assert(await toc.locator('details').evaluate(el => el.open), '页首目录按钮未展开目录');
        await page.locator('.cn-toc-toggle').click();
        assert(!(await toc.locator('details').evaluate(el => el.open)), '页首目录按钮未收起目录');
        await toc.locator('summary').click();
      }
      for (const index of [1, count - 1, Math.floor(count / 2), 1]) {
        const bodyY = await page.evaluate(({ index, width }) => {
          const links = [...document.querySelectorAll('#cn-toc-scroll a')];
          const section = document.getElementById(decodeURIComponent(links[index].hash.slice(1)));
          window.scrollTo({ top: section.getBoundingClientRect().top + scrollY - (width >= 1200 ? 99 : 139), behavior: 'instant' });
          return scrollY;
        }, { index, width });
        await page.waitForTimeout(250);
        const state = await page.evaluate(() => {
          const nav = document.querySelector('#cn-toc-scroll');
          const active = nav.querySelector('[aria-current="location"]');
          const box = nav.getBoundingClientRect();
          const item = active.getBoundingClientRect();
          return { bodyY: scrollY, visible: item.bottom <= box.bottom + 1 && item.top >= box.top - 1, href: active.hash, navY: nav.scrollTop };
        });
        assert(Math.abs(state.bodyY - bodyY) < 2, `${width}px 目录自动滚动改变了正文位置: ${bodyY} -> ${state.bodyY}，index=${index}`);
        assert(state.visible, `${width}px 当前目录项不可见 ${JSON.stringify(state)}`);
      }
      // 目录手动滚动不应带动正文。
      const beforeWheel = await page.evaluate(() => scrollY);
      await toc.locator('nav').hover();
      await page.mouse.wheel(0, -500);
      await page.waitForTimeout(150);
      assert.equal(await page.evaluate(() => scrollY), beforeWheel);
      // 锚点跳转和浏览历史。
      const anchors = await toc.locator('a').evaluateAll(links => links.slice(1, 3).map(link => link.hash));
      await page.goto(base + 'notes/basic/python-basic.html' + anchors[0]);
      await page.goto(base + 'notes/basic/python-basic.html' + anchors[1]);
      await page.goBack();
      assert.equal(new URL(page.url()).hash, anchors[0]);
      assert(await page.locator('div.highlight pre span').count() > 0, '语法高亮丢失');
      if (width < 1200) await toc.locator('details').evaluate(el => { el.open = false; });
      const copy = page.locator('button.copybtn').first();
      await copy.click();
      await page.waitForTimeout(100);
      assert((await page.evaluate(() => navigator.clipboard.readText())).length > 0, '复制结果为空');
      await page.goto(base + 'search.html?q=list', { waitUntil: 'networkidle' });
      await page.waitForSelector('#search-results li a', { timeout: 20000 });
      await page.goto(base + 'notes/basic/python-list.html#copy-lists-shallow-vs-deep-copy', { waitUntil: 'networkidle' });
      assert(await page.locator('#copy-lists-shallow-vs-deep-copy').count(), '旧锚点无效');
      await page.waitForTimeout(200);
      const anchorState = await page.locator('#copy-lists-shallow-vs-deep-copy').evaluate(el => ({ top: el.getBoundingClientRect().top, margin: getComputedStyle(el).scrollMarginTop, href: document.querySelector('#cn-toc-scroll [aria-current]').getAttribute('href') }));
      assert.equal(anchorState.href, '#copy-lists-shallow-vs-deep-copy', `直达旧锚点后目录未高亮该节：${width}px ${JSON.stringify(anchorState)}`);
      await page.goto(base, { waitUntil: 'networkidle' });
      assert(await page.locator('html').getAttribute('lang') === 'zh-CN');
      await page.goto(base + '404.html', { waitUntil: 'networkidle' });
      assert((await page.locator('h1').first().textContent()).includes('找不到'));
      assert.deepEqual(errors, [], `${width}px 浏览器或资源错误`);
      console.log(`通过 ${width}px：目录、双向滚动、正文稳定、锚点历史、复制、搜索、高亮、首页和 404`);
      await context.close();
    }
  } catch (error) { failures.push(error); }
  finally { await browser.close(); if (server) await new Promise(resolve => server.close(resolve)); }
  if (failures.length) throw failures[0];
})().catch(error => { console.error(error); process.exitCode = 1; });
