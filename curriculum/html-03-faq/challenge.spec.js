import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("FAQ begins with all answers collapsed", async ({ page }) => {
  await expect(page.getByRole('heading',{name:'Weekend FAQ',level:1})).toBeVisible();await expect(page.locator('details')).toHaveCount(3);await expect(page.locator('details[open]')).toHaveCount(0);await expect(page.locator('summary')).toHaveText(['What should I bring?','Can I join remotely?','Is there a deadline?']);await expect(page.getByText('Bring a laptop and curiosity.',{exact:true})).toBeHidden();
});

test("FAQ pointer toggles independently", async ({ page }) => {
  await page.locator('summary').nth(0).click();await expect(page.getByText('Bring a laptop and curiosity.',{exact:true})).toBeVisible();await page.locator('summary').nth(1).click();await expect(page.getByText('Yes, all exercises run locally.',{exact:true})).toBeVisible();await expect(page.locator('details[open]')).toHaveCount(2);await page.locator('summary').nth(0).click();await expect(page.getByText('Bring a laptop and curiosity.',{exact:true})).toBeHidden();await expect(page.getByText('Yes, all exercises run locally.',{exact:true})).toBeVisible();
});

test("FAQ supports native keyboard activation", async ({ page }) => {
  const summary=page.locator('summary').nth(2);await summary.focus();await summary.press('Enter');await expect(page.getByText('Finish at your own pace.',{exact:true})).toBeVisible();await summary.press('Space');await expect(page.getByText('Finish at your own pace.',{exact:true})).toBeHidden();
});
