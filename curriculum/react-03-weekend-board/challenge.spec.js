import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

// Invalid input may be rejected either by a disabled button or by ignoring the click.
async function submitIfEnabled(page,button){await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>r())));if(await button.isEnabled())await button.click();}

test("Board adds trimmed tasks and rejects blank input", async ({ page }) => {
  const input=page.getByLabel('Task',{exact:true}),add=page.getByRole('button',{name:'Add task'});
  await input.fill('   ');await submitIfEnabled(page,add);await expect(page.getByRole('list',{name:'Tasks'}).getByRole('listitem')).toHaveCount(0);
  await input.fill('  Build a parser  ');await add.click();await expect(input).toHaveValue('');
  await expect(page.getByRole('checkbox',{name:'Build a parser',exact:true})).not.toBeChecked();await expect(page.getByRole('status',{name:'Remaining'})).toHaveText('1 remaining');
});

test("Board duplicate tasks have independent identity", async ({ page }) => {
  for(let i=0;i<2;i++){await page.getByLabel('Task',{exact:true}).fill('Read docs');await page.getByRole('button',{name:'Add task'}).click();}
  const boxes=page.getByRole('checkbox',{name:'Read docs',exact:true}),remaining=page.getByRole('status',{name:'Remaining'});await boxes.first().check();await expect(boxes.nth(1)).not.toBeChecked();
  await expect(remaining).toHaveText('1 remaining');
  await boxes.first().uncheck();await expect(boxes.first()).not.toBeChecked();await expect(remaining).toHaveText('2 remaining');await boxes.nth(1).check();await expect(boxes.first()).not.toBeChecked();await expect(remaining).toHaveText('1 remaining');
  await page.getByRole('button',{name:'Delete Read docs',exact:true}).nth(1).click();await expect(boxes).toHaveCount(1);await expect(boxes.first()).not.toBeChecked();await expect(remaining).toHaveText('1 remaining');
  await page.getByLabel('Task',{exact:true}).fill('Read docs');await page.getByRole('button',{name:'Add task'}).click();await boxes.nth(1).check();await page.getByRole('button',{name:'Delete Read docs',exact:true}).first().click();await expect(boxes).toHaveCount(1);await expect(boxes.first()).toBeChecked();await expect(remaining).toHaveText('0 remaining');
});

test("Board persists completion and recovers corrupt storage", async ({ page }) => {
  for(const t of ['Ship','Later','Drop']){await page.getByLabel('Task',{exact:true}).fill(t);await page.getByRole('button',{name:'Add task'}).click();}
  await page.getByRole('checkbox',{name:'Ship',exact:true}).check();await page.getByRole('button',{name:'Delete Drop',exact:true}).click();
  await page.reload();const items=page.getByRole('list',{name:'Tasks'}).getByRole('listitem');await expect(items).toHaveCount(2);await expect(page.getByRole('checkbox',{name:'Ship',exact:true})).toBeChecked();await expect(page.getByRole('checkbox',{name:'Later',exact:true})).not.toBeChecked();await expect(page.getByRole('status',{name:'Remaining'})).toHaveText('1 remaining');
  await page.getByRole('checkbox',{name:'Ship',exact:true}).uncheck();await page.reload();await expect(page.getByRole('checkbox',{name:'Ship',exact:true})).not.toBeChecked();await expect(page.getByRole('status',{name:'Remaining'})).toHaveText('2 remaining');
  for(const bad of ['{broken','{}','"tasks"','null','[null]']){
    await page.evaluate(value=>localStorage.setItem('omagym-weekend-tasks',value),bad);await page.reload();
    await expect(page.getByRole('list',{name:'Tasks'}).getByRole('listitem'),`stored ${bad}`).toHaveCount(0);await page.getByLabel('Task',{exact:true}).fill('Recovered');await page.getByRole('button',{name:'Add task'}).click();await expect(page.getByRole('checkbox',{name:'Recovered'}),`stored ${bad}`).toBeVisible();
  }
});
