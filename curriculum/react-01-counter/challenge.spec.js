import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Counter changes reps and clamps at zero", async ({ page }) => {
  const reps=page.getByRole('status', {name:'Reps'});
  await expect(reps).toHaveText('0');
  await expect(page.getByRole('button',{name:'Remove',exact:true})).toBeDisabled();
  await page.getByRole('button',{name:'Add',exact:true}).click();
  await expect(reps).toHaveText('1');
  await page.getByLabel('Step',{exact:true}).fill('3');
  await page.getByRole('button',{name:'Remove',exact:true}).click();
  await expect(reps).toHaveText('0');
});

test("Counter resets without losing its step", async ({ page }) => {
  await page.getByLabel('Step',{exact:true}).fill('4');
  await page.getByRole('button',{name:'Add',exact:true}).click();
  await page.getByRole('button',{name:'Add',exact:true}).click();
  await expect(page.getByRole('status',{name:'Reps'})).toHaveText('8');
  await page.getByRole('button',{name:'Reset',exact:true}).click();
  await expect(page.getByRole('status',{name:'Reps'})).toHaveText('0');
  await expect(page.getByLabel('Step',{exact:true})).toHaveValue('4');
});

test("Counter rejects invalid steps and recovers", async ({ page }) => {
  for(const value of ['', '0', '-2', '1.5']) {
    await page.getByLabel('Step',{exact:true}).fill(value);
    await expect(page.getByRole('button',{name:'Add',exact:true})).toBeDisabled();
    await expect(page.getByRole('button',{name:'Remove',exact:true})).toBeDisabled();
  }
  await page.getByLabel('Step',{exact:true}).fill('2');
  await page.getByRole('button',{name:'Add',exact:true}).click();
  await expect(page.getByRole('status',{name:'Reps'})).toHaveText('2');
});
