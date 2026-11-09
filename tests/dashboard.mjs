// Run after npm run build. All requests stay in fixtures; no live gym is used.
import { readFile } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import { test } from 'node:test';
import { chromium, expect } from '@playwright/test';

const build = resolve('dist/client');
const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', headless: true });

async function dashboard(t, failPath = '') {
  const context = await browser.newContext();
  t.after(() => context.close());
  const page = await context.newPage();
  await page.addInitScript(() => {
    Object.defineProperty(document, 'modelContext', { value: {
      registerTool(tool) { window.practiceTool = tool; },
    } });
  });
  const fixture = {
    project: { id: 'practice', title: 'Practice fixture', track: 'go', entry: 'main.go', runner: 'go', level: 'Beginner', summary: 'Test fixture', skills: [], requirements: [], docs: [],
      run: { passed: true, stale: false, fingerprint: 'original', elapsed: 0.1, tests: [{ name: 'counts words', action: 'pass' }], output: 'Passed' } },
    writes: [],
    failPath,
    otherProjects: [],
  };
  await page.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (url.origin !== 'http://omagym.test') return route.abort();
    if (url.pathname === fixture.failPath) {
      fixture.failPath = '';
      return route.fulfill({ status: 503, json: { error: 'Temporary connection failure' } });
    }
    if (url.pathname === '/api/projects') return route.fulfill({ json: { projects: [fixture.project, ...fixture.otherProjects] } });
    if (url.pathname === '/api/files') return route.fulfill({ json: { files: [{ path: 'main.go', editable: true }] } });
    if (url.pathname === '/api/file') {
      if (route.request().method() !== 'GET') {
        fixture.writes.push(route.request().postDataJSON());
        return route.fulfill({ status: 409, json: { error: 'File changed on disk. Reopen it before saving.' } });
      }
      return route.fulfill({ json: { content: 'package main\n', revision: 'original', editable: true } });
    }
    if (url.pathname.startsWith('/api/')) return route.fulfill({ status: 404, json: { error: 'Unexpected fixture request' } });
    const path = resolve(build, '.' + (url.pathname === '/' ? '/index.html' : decodeURIComponent(url.pathname)));
    if (!path.startsWith(build + sep)) return route.abort();
    try {
      const contentType = path.endsWith('.js') ? 'application/javascript' : path.endsWith('.css') ? 'text/css' : path.endsWith('.html') ? 'text/html' : 'application/octet-stream';
      await route.fulfill({ body: await readFile(path), contentType });
    } catch { await route.fulfill({ status: 404 }); }
  });
  await page.goto('http://omagym.test');
  return { page, fixture };
}

try {
  for (const destination of ['file', 'project', 'track', 'create']) await test(`a missing entry file does not block ${destination} navigation`, async t => {
    const { page, fixture } = await dashboard(t);
    await expect(page.locator('.cm-content')).toBeVisible();
    fixture.otherProjects.push({ ...fixture.project, id: 'healthy', title: 'Healthy exercise', track: destination === 'track' ? 'javascript' : 'go' });
    await page.route('**/api/files?*', route => route.fulfill({ json: { files: [{ path: 'helper.go', editable: true }] } }));
    await page.route(/\/api\/file(?:\?|$)/, route => {
      const query = new URL(route.request().url()).searchParams;
      if (route.request().method() !== 'GET') {
        fixture.writes.push(route.request().postDataJSON());
        return route.fulfill({ json: { revision: 'created' } });
      }
      return !fixture.writes.length && query.get('project') === 'practice' && query.get('path') === 'main.go'
        ? route.fulfill({ status: 404, json: { error: 'Entry file is missing' } })
        : route.fulfill({ json: { content: '// Healthy file', revision: 'healthy', editable: true } });
    });
    await page.reload();
    await expect(page.getByRole('alert')).toContainText('Entry file is missing');
    if (destination === 'file') await page.getByRole('button', { name: 'helper.go', exact: true }).click({ timeout: 3000 });
    else if (destination === 'project') await page.getByRole('button', { name: /Healthy exercise/ }).click({ timeout: 3000 });
    else if (destination === 'create') {
      await page.getByRole('button', { name: 'New file', exact: true }).click({ timeout: 3000 });
      await page.getByRole('textbox', { name: 'New file path' }).fill('main.go');
      await page.getByRole('button', { name: 'Create', exact: true }).click();
    }
    else await page.getByRole('combobox', { name: 'Language or framework' }).selectOption('javascript', { timeout: 3000 });
    await expect(page.locator('.cm-content')).toHaveText('// Healthy file');
    await expect(page.getByRole('alert')).toHaveCount(0);
    expect(fixture.writes).toEqual(destination === 'create' ? [{ project: 'practice', path: 'main.go', content: '', create: true }] : []);
  });
  await test('inspection omits the previous draft when the selected file is unreadable', async t => {
    const { page, fixture } = await dashboard(t);
    await expect(page.locator('.cm-content')).toBeVisible();
    fixture.otherProjects.push({ ...fixture.project, id: 'missing', title: 'Missing exercise' });
    await page.evaluate(() => window.dispatchEvent(new Event('focus')));
    await page.route('**/api/file?project=missing*', route => route.fulfill({ status: 404, json: { error: 'Entry file is missing' } }));
    await page.getByRole('button', { name: /Missing exercise/ }).click();
    await expect(page.getByRole('alert')).toContainText('Entry file is missing');
    const state = await page.evaluate(() => window.practiceTool.execute({}));
    expect(state.project.id).toBe('missing');
    expect(state.draft).toBeNull();
    expect(fixture.writes).toHaveLength(0);
  });
  await test('leaving a pending file load keeps the new project and its file list', async t => {
    const { page, fixture } = await dashboard(t);
    await expect(page.locator('.cm-content')).toBeVisible();
    fixture.otherProjects.push({ ...fixture.project, id: 'healthy', title: 'Healthy exercise' });
    await page.route('**/api/files?*', route => {
      const practice = new URL(route.request().url()).searchParams.get('project') === 'practice';
      return route.fulfill({ json: { files: [{ path: practice ? 'slow.go' : 'healthy.go', editable: true }] } });
    });
    let release;
    await page.route('**/api/file?*', async route => {
      const query = new URL(route.request().url()).searchParams;
      if (query.get('path') === 'slow.go') await new Promise(resolve => { release = resolve; });
      await route.fulfill({ json: { content: '// ' + query.get('project'), revision: 'fixture', editable: true } });
    });
    await page.reload();
    await expect(page.locator('.cm-content')).toHaveText('// practice');
    await page.getByRole('button', { name: 'slow.go', exact: true }).click();
    await expect.poll(() => typeof release).toBe('function');
    await page.getByRole('button', { name: /Healthy exercise/ }).click({ timeout: 3000 });
    await expect(page.locator('.cm-content')).toHaveText('// healthy');
    await expect(page.getByRole('button', { name: 'healthy.go', exact: true })).toBeVisible();
    const response = page.waitForResponse(url => new URL(url.url()).searchParams.get('path') === 'slow.go');
    release();
    await (await response).finished();
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    await expect(page.locator('.cm-content')).toHaveText('// healthy');
    await expect(page.getByRole('button', { name: 'slow.go', exact: true })).toHaveCount(0);
    expect(fixture.writes).toHaveLength(0);
  });
  for (const path of ['/api/projects', '/api/file']) for (const trigger of ['retry', 'focus']) {
    await test(`dashboard recovers after ${path} fails on ${trigger}`, async t => {
      const { page } = await dashboard(t, path);
      await expect(page.getByRole('alert')).toContainText('Temporary connection failure');
      if (trigger === 'retry') await page.getByRole('button', { name: 'Retry connection' }).click({ timeout: 3000 });
      else await page.evaluate(() => window.dispatchEvent(new Event('focus')));
      await expect(page.getByRole('button', { name: 'Run tests', exact: true })).toBeEnabled();
      await expect(page.locator('.cm-content')).toHaveText('package main');
      await expect(page.getByRole('alert')).toHaveCount(0);
    });
  }
  for (const operation of ['run', 'save']) await test(`a delayed project refresh cannot replace a newer ${operation} verdict`, async t => {
    const { page, fixture } = await dashboard(t);
    await expect(page.locator('.cm-content')).toBeVisible();
    await page.getByRole('tab', { name: 'Tests', exact: true }).click();
    const previous = structuredClone(fixture.project);
    let release;
    await page.route('**/api/projects', async route => {
      await new Promise(resolve => { release = resolve; });
      await route.fulfill({ json: { projects: [previous] } });
    }, { times: 1 });
    await page.evaluate(() => window.dispatchEvent(new Event('focus')));
    await expect.poll(() => typeof release).toBe('function');
    if (operation === 'run') {
      fixture.project.run = { ...fixture.project.run, passed: false, tests: [{ name: 'counts words', action: 'fail' }], output: 'Failed' };
      await page.route('**/api/run', route => route.fulfill({ json: fixture.project.run }));
      await page.getByRole('button', { name: 'Run tests', exact: true }).click();
    } else {
      await page.locator('.cm-content').fill('package main\n// Saved change');
      await page.route('**/api/file', route => route.fulfill({ json: { content: route.request().postDataJSON().content, revision: 'saved', editable: true } }));
      await page.getByRole('button', { name: 'Save', exact: true }).click();
      await expect(page.locator('.editor-status')).toContainText('Saved on disk');
    }
    const verdict = page.getByRole('heading', { name: operation === 'run' ? 'Keep going.' : 'Code changed', exact: true });
    await expect(verdict).toBeVisible();
    const response = page.waitForResponse('**/api/projects');
    release();
    await (await response).finished();
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    await expect(verdict).toBeVisible();
  });
  await test('returning to the dashboard refreshes verdicts without losing drafts or bypassing save conflicts', async t => {
    const { page, fixture } = await dashboard(t);
    await expect(page.locator('.cm-content')).toBeVisible();
    await page.getByRole('tab', { name: 'Tests', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'All checks passed' })).toBeVisible();
    fixture.project.run.stale = true;
    await page.evaluate(() => window.dispatchEvent(new Event('focus')));
    await expect(page.getByRole('heading', { name: 'Code changed' })).toBeVisible();
    await page.locator('.cm-content').fill('package main\n// Keep my unsaved draft');
    fixture.failPath = '/api/projects';
    await page.evaluate(() => window.dispatchEvent(new Event('focus')));
    await expect(page.getByRole('alert')).toContainText('Temporary connection failure');
    await page.getByRole('button', { name: 'Retry connection' }).click();
    await expect(page.getByRole('alert')).toHaveCount(0);
    await expect(page.locator('.cm-content')).toContainText('Keep my unsaved draft');
    await page.getByRole('button', { name: 'Save', exact: true }).click();
    await expect(page.getByRole('alert')).toContainText('File changed on disk');
    await page.evaluate(() => window.dispatchEvent(new Event('focus')));
    await expect(page.getByRole('alert')).toContainText('File changed on disk');
    await expect(page.locator('.cm-content')).toContainText('Keep my unsaved draft');
    expect(fixture.writes).toHaveLength(1);
    expect(fixture.writes[0].revision).toBe('original');
  });
} finally { await browser.close(); }
