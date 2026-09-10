import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Cart computes decimal totals from both quantities", async ({ page }) => {
  await expect(page.getByRole('status',{name:'Total'})).toHaveText('€0.00');await expect(page.getByRole('button',{name:'Checkout'})).toBeDisabled();
  await page.getByLabel('Apples quantity').fill('2');await page.getByLabel('Nuts quantity').fill('3');await expect(page.getByRole('status',{name:'Total'})).toHaveText('€9.75');await expect(page.getByRole('button',{name:'Checkout'})).toBeEnabled();
});

test("Cart rejects invalid quantities and recovers", async ({ page }) => {
  for(const bad of ['','-1','11','1.5']){await page.getByLabel('Apples quantity').fill(bad);await expect(page.getByRole('button',{name:'Checkout'})).toBeDisabled();await expect(page.getByText('Invalid quantity',{exact:true})).toBeVisible();}
  await page.getByLabel('Apples quantity').fill('1');
  for(const bad of ['', '-1', '11', '1.5']){await page.getByLabel('Nuts quantity').fill(bad);await expect(page.getByRole('button',{name:'Checkout'})).toBeDisabled();}
  await page.getByLabel('Nuts quantity').fill('0');await page.getByLabel('Apples quantity').fill('10');await expect(page.getByRole('status',{name:'Total'})).toHaveText('€15.00');await expect(page.getByRole('button',{name:'Checkout'})).toBeEnabled();
});

test("Cart checkout confirms and clears quantities", async ({ page }) => {
  await page.getByLabel('Nuts quantity').fill('2');await page.getByRole('button',{name:'Checkout'}).click();await expect(page.getByText('Order placed',{exact:true})).toBeVisible();await expect(page.getByLabel('Apples quantity')).toHaveValue('0');await expect(page.getByLabel('Nuts quantity')).toHaveValue('0');await expect(page.getByRole('status',{name:'Total'})).toHaveText('€0.00');await expect(page.getByRole('button',{name:'Checkout'})).toBeDisabled();
});
