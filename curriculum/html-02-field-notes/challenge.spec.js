import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Article exposes landmarks and a logical heading hierarchy", async ({ page }) => {
  await expect(page.getByRole('banner')).toHaveCount(1);await expect(page.getByRole('banner').getByRole('navigation',{name:'Main'})).toBeVisible();const main=page.getByRole('main');await expect(main).toHaveAttribute('id','notes');await expect(page.getByRole('article')).toHaveCount(1);await expect(main.getByRole('article')).toHaveCount(1);await expect(page.getByRole('heading',{level:1})).toHaveText('Learning in public');await expect(main.getByRole('heading',{level:1})).toHaveText('Learning in public');await expect(page.getByRole('heading',{level:2})).toHaveText(['Notes','Schedule']);await expect(main.getByRole('heading',{level:2})).toHaveText(['Notes','Schedule']);await expect(page.getByRole('contentinfo')).toHaveCount(1);
});

test("Article navigation and media carry useful semantics", async ({ page }) => {
  const nav=page.getByRole('banner').getByRole('navigation',{name:'Main'});await nav.getByRole('link',{name:'Schedule',exact:true}).click();await expect(page).toHaveURL(/#schedule$/);await expect(page.locator('#schedule')).toBeVisible();await expect(page.getByRole('main').locator('#schedule')).toHaveCount(1);await nav.getByRole('link',{name:'Notes',exact:true}).click();await expect(page).toHaveURL(/#notes$/);
  const article=page.getByRole('article');await expect(article.locator('time')).toHaveAttribute('datetime','2026-09-12');await expect(article.locator('time')).toHaveText('12 September 2026');const figure=article.locator('figure');await expect(figure).toHaveCount(1);await expect(figure.getByRole('img',{name:'Desk with a notebook'})).toBeVisible();await expect(figure.locator('figcaption')).toHaveText('Weekend setup');
});

test("Article table supports header relationships", async ({ page }) => {
  const table=page.getByRole('table',{name:'Weekend schedule'});await expect(table).toHaveCount(1);expect(await table.evaluate(t=>t.caption?.textContent.trim())).toBe('Weekend schedule');await expect(table.getByRole('columnheader')).toHaveText(['Day','Focus']);await expect(table.getByRole('rowheader')).toHaveText(['Saturday','Sunday']);for(const h of await table.getByRole('columnheader').all())await expect(h).toHaveAttribute('scope','col');for(const h of await table.getByRole('rowheader').all())await expect(h).toHaveAttribute('scope','row');
  for(const [i,day,focus] of [[1,'Saturday','Build'],[2,'Sunday','Reflect']]){const row=table.getByRole('row').nth(i);await expect(row.getByRole('rowheader')).toHaveText(day);await expect(row.getByRole('cell')).toHaveText([focus]);}
});
