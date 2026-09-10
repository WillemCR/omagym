import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Board adds trimmed tasks and rejects blank input", async ({ page }) => {
  const input=page.getByLabel('Task',{exact:true}),add=page.getByRole('button',{name:'Add task'});
  await input.fill('   ');await add.click();await expect(page.getByRole('list',{name:'Tasks'}).getByRole('listitem')).toHaveCount(0);
  await input.fill('  Build a parser  ');await add.click();await expect(input).toHaveValue('');
  await expect(page.getByRole('checkbox',{name:'Build a parser',exact:true})).not.toBeChecked();await expect(page.getByRole('status',{name:'Remaining'})).toHaveText('1 remaining');
});

test("Board duplicate tasks have independent identity", async ({ page }) => {
  for(let i=0;i<2;i++){await page.getByLabel('Task',{exact:true}).fill('Read docs');await page.getByRole('button',{name:'Add task'}).click();}
  const boxes=page.getByRole('checkbox',{name:'Read docs',exact:true});await boxes.first().check();await expect(boxes.nth(1)).not.toBeChecked();
  await expect(page.getByRole('status',{name:'Remaining'})).toHaveText('1 remaining');
  await page.getByRole('button',{name:'Delete Read docs',exact:true}).first().click();await expect(boxes).toHaveCount(1);await expect(boxes.first()).not.toBeChecked();
});

test("Board persists completion and recovers corrupt storage", async ({ page }) => {
  await page.getByLabel('Task',{exact:true}).fill('Ship');await page.getByRole('button',{name:'Add task'}).click();await page.getByRole('checkbox',{name:'Ship',exact:true}).check();
  await page.reload();await expect(page.getByRole('checkbox',{name:'Ship',exact:true})).toBeChecked();await expect(page.getByRole('status',{name:'Remaining'})).toHaveText('0 remaining');
  await page.evaluate(()=>localStorage.setItem('omagym-weekend-tasks','{broken'));await page.reload();
  await expect(page.getByRole('list',{name:'Tasks'}).getByRole('listitem')).toHaveCount(0);await page.getByLabel('Task',{exact:true}).fill('Recovered');await page.getByRole('button',{name:'Add task'}).click();await expect(page.getByRole('checkbox',{name:'Recovered'})).toBeVisible();
});
