import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Budget accepts trimmed expenses and rejects invalid amounts", async ({ page }) => {
  await page.getByLabel('Description',{exact:true}).fill('   ');await page.getByLabel('Amount',{exact:true}).fill('5');await page.getByRole('button',{name:'Add expense'}).click();await expect(page.getByRole('list',{name:'Expenses'}).getByRole('listitem')).toHaveCount(0);
  await page.getByLabel('Description',{exact:true}).fill(' Coffee ');for(const v of ['0','-2','']){await page.getByLabel('Amount',{exact:true}).fill(v);await page.getByRole('button',{name:'Add expense'}).click();await expect(page.getByRole('list',{name:'Expenses'}).getByRole('listitem')).toHaveCount(0);}
  await page.getByLabel('Amount',{exact:true}).fill('3.5');await page.getByRole('button',{name:'Add expense'}).click();await expect(page.getByRole('listitem')).toContainText('Coffee');await expect(page.getByRole('listitem')).toContainText('3.50');await expect(page.getByLabel('Description',{exact:true})).toHaveValue('');await expect(page.getByLabel('Amount',{exact:true})).toHaveValue('');
});

test("Budget filters rows but retains overall total", async ({ page }) => {
  for(const [desc,amount,cat] of [['Lunch','8.25','Food'],['Train','12','Travel']]){await page.getByLabel('Description',{exact:true}).fill(desc);await page.getByLabel('Amount',{exact:true}).fill(amount);await page.getByLabel('Category',{exact:true}).selectOption(cat);await page.getByRole('button',{name:'Add expense'}).click();}
  await page.getByLabel('Filter category',{exact:true}).selectOption('Travel');await expect(page.getByRole('listitem')).toHaveCount(1);await expect(page.getByRole('listitem')).toContainText('Train');await expect(page.getByRole('status',{name:'Total',exact:true})).toHaveText('€20.25');await expect(page.getByRole('status',{name:'Visible total',exact:true})).toHaveText('€12.00');await page.getByLabel('Filter category',{exact:true}).selectOption('Fun');await expect(page.getByText('No expenses',{exact:true})).toBeVisible();await expect(page.getByRole('status',{name:'Visible total',exact:true})).toHaveText('€0.00');
});

test("Budget removes only the selected duplicate", async ({ page }) => {
  for(const amount of ['2','4']){await page.getByLabel('Description',{exact:true}).fill('Snack');await page.getByLabel('Amount',{exact:true}).fill(amount);await page.getByRole('button',{name:'Add expense'}).click();}
  await page.getByRole('button',{name:'Remove Snack',exact:true}).first().click();await expect(page.getByRole('listitem')).toHaveCount(1);await expect(page.getByRole('status',{name:'Total',exact:true})).toHaveText('€4.00');await page.getByRole('button',{name:'Remove Snack',exact:true}).click();await expect(page.getByRole('status',{name:'Total',exact:true})).toHaveText('€0.00');
});
