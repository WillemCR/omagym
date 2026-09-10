import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Registration exposes native labelled fields", async ({ page }) => {
  const form=page.getByRole('form',{name:'Workshop registration'});await expect(form).toBeVisible();await expect(page.getByLabel('Tickets',{exact:true})).toHaveValue('1');await expect(page.getByLabel('Track',{exact:true})).toHaveValue('go');await expect(page.getByRole('button',{name:'Register',exact:true})).toHaveAttribute('type','submit');await expect(form).not.toHaveJSProperty('noValidate',true);expect(await form.evaluate(f=>f.checkValidity())).toBe(false);
});

test("Registration validates email tickets and terms", async ({ page }) => {
  const form=page.getByRole('form',{name:'Workshop registration'});await page.getByLabel('Name',{exact:true}).fill('Willem');await page.getByLabel('Email',{exact:true}).fill('not-an-email');await page.getByLabel('Accept terms',{exact:true}).check();expect(await form.evaluate(f=>f.checkValidity())).toBe(false);await page.getByLabel('Email',{exact:true}).fill('w@example.com');
  for(const n of ['0','5','1.5']){await page.getByLabel('Tickets',{exact:true}).fill(n);expect(await form.evaluate(f=>f.checkValidity())).toBe(false);}
  await page.getByLabel('Tickets',{exact:true}).fill('4');expect(await form.evaluate(f=>f.checkValidity())).toBe(true);for(const [label,value] of [['Name','Willem'],['Email','w@example.com'],['Tickets','4']]){await page.getByLabel(label,{exact:true}).fill('');expect(await form.evaluate(f=>f.checkValidity())).toBe(false);await page.getByLabel(label,{exact:true}).fill(value);}
  await page.getByLabel('Accept terms',{exact:true}).uncheck();expect(await form.evaluate(f=>f.checkValidity())).toBe(false);
});

test("Registration produces useful form data", async ({ page }) => {
  await page.getByLabel('Name',{exact:true}).fill('Ada');await page.getByLabel('Email',{exact:true}).fill('ada@example.com');await page.getByLabel('Tickets',{exact:true}).fill('2');await page.getByLabel('Track',{exact:true}).selectOption('rust');await page.getByLabel('Accept terms',{exact:true}).check();
  const data=await page.getByRole('form',{name:'Workshop registration'}).evaluate(f=>Object.fromEntries(new FormData(f)));expect(data).toMatchObject({name:'Ada',email:'ada@example.com',tickets:'2',track:'rust'});expect(data).toHaveProperty('terms');
});
