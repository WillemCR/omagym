import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Article exposes landmarks and a logical heading hierarchy", async ({ page }) => {
  await expect(page.getByRole('banner')).toHaveCount(1);await expect(page.getByRole('navigation',{name:'Main'})).toBeVisible();await expect(page.getByRole('main')).toHaveAttribute('id','notes');await expect(page.getByRole('article')).toHaveCount(1);await expect(page.getByRole('heading',{level:1})).toHaveText('Learning in public');await expect(page.getByRole('heading',{level:2})).toHaveText(['Notes','Schedule']);await expect(page.getByRole('contentinfo')).toHaveCount(1);
});

test("Article navigation and media carry useful semantics", async ({ page }) => {
  await page.getByRole('link',{name:'Schedule',exact:true}).click();await expect(page).toHaveURL(/#schedule$/);await expect(page.locator('#schedule')).toBeVisible();await page.getByRole('link',{name:'Notes',exact:true}).click();await expect(page).toHaveURL(/#notes$/);await expect(page.locator('article time')).toHaveAttribute('datetime','2026-09-12');await expect(page.locator('article time')).toHaveText('12 September 2026');await expect(page.getByRole('img',{name:'Desk with a notebook'})).toBeVisible();await expect(page.locator('figure figcaption')).toHaveText('Weekend setup');
});

test("Article table supports header relationships", async ({ page }) => {
  const table=page.getByRole('table',{name:'Weekend schedule'});await expect(table.getByRole('columnheader')).toHaveText(['Day','Focus']);await expect(table.getByRole('rowheader')).toHaveText(['Saturday','Sunday']);for(const h of await table.getByRole('columnheader').all())await expect(h).toHaveAttribute('scope','col');for(const h of await table.getByRole('rowheader').all())await expect(h).toHaveAttribute('scope','row');await expect(table.getByRole('row').nth(1)).toContainText('Build');await expect(table.getByRole('row').nth(2)).toContainText('Reflect');
});
