import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Directory filters names without case or whitespace surprises", async ({ page }) => {
  const rows=page.getByRole('list',{name:'Languages'}).getByRole('listitem');
  await expect(rows).toHaveCount(4);
  await page.getByLabel('Search',{exact:true}).fill('  SCRIPT  ');
  await expect(rows).toHaveCount(1); await expect(rows.first()).toContainText('JavaScript');
  await expect(page.getByRole('status',{name:'Result count'})).toHaveText('1 results');
});

test("Directory combines category and search", async ({ page }) => {
  await page.getByRole('combobox',{name:/^Category\b/}).selectOption({label:'Systems'});
  const rows=page.getByRole('list',{name:'Languages'}).getByRole('listitem');
  await expect(rows).toHaveCount(2); await expect(rows.nth(0)).toContainText('Rust'); await expect(rows.nth(1)).toContainText('Go');
  for(const i of [0,1]) await expect(rows.nth(i)).toContainText('Systems');
  await page.getByRole('combobox',{name:/^Category\b/}).selectOption({label:'Scripting'});
  await expect(rows).toHaveCount(2); await expect(rows.nth(0)).toContainText('JavaScript'); await expect(rows.nth(1)).toContainText('Python');
  for(const i of [0,1]) await expect(rows.nth(i)).toContainText('Scripting');
  await expect(page.getByRole('status',{name:'Result count'})).toHaveText('2 results');
  await page.getByLabel('Search',{exact:true}).fill('o');
  await expect(rows).toHaveCount(1); await expect(rows.first()).toContainText('Python');
  await page.getByLabel('Search',{exact:true}).fill('');
  await page.getByRole('combobox',{name:/^Category\b/}).selectOption({label:'Systems'});
  await page.getByLabel('Search',{exact:true}).fill('python');
  await expect(rows).toHaveCount(0); await expect(page.getByText('No languages found',{exact:true})).toBeVisible();
  await expect(page.getByRole('status',{name:'Result count'})).toHaveText('0 results');
});

test("Directory clear restores input and original order", async ({ page }) => {
  await page.getByLabel('Search',{exact:true}).fill('go'); await page.getByRole('combobox',{name:/^Category\b/}).selectOption({label:'Scripting'});
  await page.getByRole('button',{name:'Clear filters'}).click();
  await expect(page.getByLabel('Search',{exact:true})).toHaveValue(''); await expect.poll(()=>page.getByRole('combobox',{name:/^Category\b/}).evaluate(s=>s.selectedOptions[0]?.textContent.trim())).toBe('All');
  const rows=page.getByRole('list',{name:'Languages'}).getByRole('listitem');await expect(rows).toHaveCount(4);await expect(page.getByText('No languages found',{exact:true})).toBeHidden();
  for(const [i,name] of ['Rust','Go','JavaScript','Python'].entries()) await expect(rows.nth(i)).toContainText(name);
});
