import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Tabs start with one selected panel", async ({ page }) => {
  await expect(page.getByRole('tablist',{name:'Reading guide'})).toBeVisible();await expect(page.getByRole('tab')).toHaveCount(3);await expect(page.getByRole('tab',{name:'Overview',exact:true})).toHaveAttribute('aria-selected','true');await expect(page.getByRole('tabpanel',{name:'Overview',exact:true})).toHaveText('Welcome to Vue');await expect(page.getByRole('tabpanel')).toHaveCount(1);await expect(page.locator('[role="tab"][aria-selected="true"]')).toHaveCount(1);
});

test("Tabs respond to clicks and expose selection", async ({ page }) => {
  await page.getByRole('tab',{name:'Examples',exact:true}).click();await expect(page.getByRole('tabpanel',{name:'Examples',exact:true})).toHaveText('Practice makes progress');await expect(page.getByRole('tab',{name:'Examples',exact:true})).toHaveAttribute('aria-selected','true');await expect(page.getByRole('tab',{name:'Overview',exact:true})).toHaveAttribute('aria-selected','false');await expect(page.getByRole('tab',{name:'Overview',exact:true})).toHaveAttribute('tabindex','-1');
});

test("Tabs keyboard wraps and supports home and end", async ({ page }) => {
  const overview=page.getByRole('tab',{name:'Overview',exact:true});await overview.focus();await overview.press('ArrowLeft');const resources=page.getByRole('tab',{name:'Resources',exact:true});await expect(resources).toBeFocused();await expect(page.getByRole('tabpanel',{name:'Resources'})).toHaveText('Read the official guide');await resources.press('ArrowRight');await expect(overview).toBeFocused();await overview.press('End');await expect(resources).toBeFocused();await resources.press('Home');await expect(overview).toBeFocused();await overview.press('ArrowRight');await expect(page.getByRole('tab',{name:'Examples',exact:true})).toBeFocused();await expect(page.locator('[role="tab"][tabindex="0"]')).toHaveCount(1);
});
