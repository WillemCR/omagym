import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

// Invalid input may be rejected either by a disabled button or by ignoring the click.
async function submitIfEnabled(page,button){await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>r())));if(await button.isEnabled())await button.click();}

test("Budget accepts trimmed expenses and rejects invalid amounts", async ({ page }) => {
  await page.getByLabel('Description',{exact:true}).fill('   ');await page.getByLabel('Amount',{exact:true}).fill('5');await submitIfEnabled(page,page.getByRole('button',{name:'Add expense'}));await expect(page.getByRole('list',{name:'Expenses'}).getByRole('listitem')).toHaveCount(0);
  await page.getByLabel('Description',{exact:true}).fill(' Coffee ');for(const v of ['0','-2','']){await page.getByLabel('Amount',{exact:true}).fill(v);await submitIfEnabled(page,page.getByRole('button',{name:'Add expense'}));await expect(page.getByRole('list',{name:'Expenses'}).getByRole('listitem')).toHaveCount(0);}
  await page.getByLabel('Amount',{exact:true}).fill('3.5');await page.getByRole('button',{name:'Add expense'}).click();await expect(page.getByRole('listitem')).toContainText('Coffee');await expect(page.getByRole('listitem')).toContainText('3.50');await expect(page.getByLabel('Description',{exact:true})).toHaveValue('');await expect(page.getByLabel('Amount',{exact:true})).toHaveValue('');
});

test("Budget filters rows but retains overall total", async ({ page }) => {
  for(const [desc,amount,cat] of [['Lunch','8.25','Food'],['Train','12','Travel']]){await page.getByLabel('Description',{exact:true}).fill(desc);await page.getByLabel('Amount',{exact:true}).fill(amount);await page.getByRole('combobox',{name:/^Category\b/}).selectOption(cat);await page.getByRole('button',{name:'Add expense'}).click();}
  await page.getByRole('combobox',{name:/^Filter category\b/}).selectOption('Travel');await expect(page.getByRole('listitem')).toHaveCount(1);await expect(page.getByRole('listitem')).toContainText('Train');await expect(page.getByRole('status',{name:'Total',exact:true})).toHaveText('€20.25');await expect(page.getByRole('status',{name:'Visible total',exact:true})).toHaveText('€12.00');await page.getByRole('combobox',{name:/^Filter category\b/}).selectOption('Fun');await expect(page.getByText('No expenses',{exact:true})).toBeVisible();await expect(page.getByRole('status',{name:'Visible total',exact:true})).toHaveText('€0.00');
  await page.getByLabel('Description',{exact:true}).fill('Cinema');await page.getByLabel('Amount',{exact:true}).fill('9');await page.getByRole('combobox',{name:/^Category\b/}).selectOption('Fun');await page.getByRole('button',{name:'Add expense'}).click();await expect(page.getByRole('listitem')).toHaveCount(1);await expect(page.getByRole('listitem')).toContainText('Cinema');await expect(page.getByText('No expenses',{exact:true})).toBeHidden();await expect(page.getByRole('status',{name:'Visible total',exact:true})).toHaveText('€9.00');await expect(page.getByRole('status',{name:'Total',exact:true})).toHaveText('€29.25');
});

test("Budget removes only the selected duplicate", async ({ page }) => {
  for(const amount of ['2','4']){await page.getByLabel('Description',{exact:true}).fill('Snack');await page.getByLabel('Amount',{exact:true}).fill(amount);await page.getByRole('button',{name:'Add expense'}).click();}
  const total=page.getByRole('status',{name:'Total',exact:true}),visible=page.getByRole('status',{name:'Visible total',exact:true});
  await page.getByRole('button',{name:'Remove Snack',exact:true}).nth(1).click();await expect(page.getByRole('listitem')).toHaveCount(1);await expect(page.getByRole('listitem')).toContainText('2.00');await expect(total).toHaveText('€2.00');await page.getByRole('button',{name:'Remove Snack',exact:true}).click();await expect(total).toHaveText('€0.00');
  for(const [desc,amount,cat] of [['Lunch','8.25','Food'],['Train','12','Travel'],['Bus','3','Travel']]){await page.getByLabel('Description',{exact:true}).fill(desc);await page.getByLabel('Amount',{exact:true}).fill(amount);await page.getByRole('combobox',{name:/^Category\b/}).selectOption(cat);await page.getByRole('button',{name:'Add expense'}).click();}
  await page.getByRole('combobox',{name:/^Filter category\b/}).selectOption('Travel');await page.getByRole('button',{name:'Remove Bus',exact:true}).click();await expect(page.getByRole('listitem')).toHaveCount(1);await expect(page.getByRole('listitem')).toContainText('Train');await expect(total).toHaveText('€20.25');await expect(visible).toHaveText('€12.00');
  await page.getByRole('combobox',{name:/^Filter category\b/}).selectOption('All');await expect(page.getByRole('listitem')).toHaveCount(2);await expect(page.getByRole('listitem').nth(0)).toContainText('Lunch');await expect(page.getByRole('listitem').nth(1)).toContainText('Train');await expect(visible).toHaveText('€20.25');
});
