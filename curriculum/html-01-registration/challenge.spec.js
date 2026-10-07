import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

// A label wrapping a <select> also contains its option text, so the select is found by role and name prefix.
const control=(page,label)=>label==='Track'?page.getByRole('combobox',{name:/^Track\b/}):page.getByLabel(label,{exact:true});

test("Registration exposes native labelled fields", async ({ page }) => {
  const form=page.getByRole('form',{name:'Workshop registration'});await expect(form).toBeVisible();await expect(page.getByLabel('Tickets',{exact:true})).toHaveValue('1');await expect(page.getByRole('combobox',{name:/^Track\b/})).toHaveValue('go');const register=page.getByRole('button',{name:'Register',exact:true});await expect(register).toHaveJSProperty('type','submit');expect(await register.evaluate(b=>b.form!==null)).toBe(true);await expect(form).not.toHaveJSProperty('noValidate',true);expect(await form.evaluate(f=>f.checkValidity())).toBe(false);
  for(const [label,type] of [['Name','text'],['Email','email'],['Tickets','number'],['Track','select-one'],['Accept terms','checkbox']])await expect(control(page,label)).toHaveJSProperty('type',type);
  for(const label of ['Name','Email','Tickets','Track']){const field=control(page,label);const native=await field.evaluateHandle(e=>e.labels?.[0]??null);expect(await native.evaluate(l=>l!==null),`${label} needs a native label`).toBe(true);await page.evaluate(()=>document.activeElement?.blur());await native.asElement().click();await expect(field).toBeFocused();}
  const terms=page.getByLabel('Accept terms',{exact:true}),termsLabel=await terms.evaluateHandle(e=>e.labels?.[0]??null);expect(await termsLabel.evaluate(l=>l!==null),'Accept terms needs a native label').toBe(true);await termsLabel.asElement().click();await expect(terms).toBeChecked();await termsLabel.asElement().click();await expect(terms).not.toBeChecked();
});

test("Registration validates email tickets and terms", async ({ page }) => {
  const form=page.getByRole('form',{name:'Workshop registration'});await page.getByLabel('Name',{exact:true}).fill('Willem');await page.getByLabel('Email',{exact:true}).fill('not-an-email');await page.getByLabel('Accept terms',{exact:true}).check();expect(await form.evaluate(f=>f.checkValidity())).toBe(false);await page.getByLabel('Email',{exact:true}).fill('w@example.com');
  for(const n of ['0','5','1.5']){await page.getByLabel('Tickets',{exact:true}).fill(n);expect(await form.evaluate(f=>f.checkValidity())).toBe(false);}
  await page.getByLabel('Tickets',{exact:true}).fill('4');expect(await form.evaluate(f=>f.checkValidity())).toBe(true);for(const [label,value] of [['Name','Willem'],['Email','w@example.com'],['Tickets','4']]){await page.getByLabel(label,{exact:true}).fill('');expect(await form.evaluate(f=>f.checkValidity())).toBe(false);await page.getByLabel(label,{exact:true}).fill(value);}
  await page.getByLabel('Accept terms',{exact:true}).uncheck();expect(await form.evaluate(f=>f.checkValidity())).toBe(false);
});

test("Registration produces useful form data", async ({ page }) => {
  await page.getByLabel('Name',{exact:true}).fill('Ada');await page.getByLabel('Email',{exact:true}).fill('ada@example.com');await page.getByLabel('Tickets',{exact:true}).fill('2');await page.getByRole('combobox',{name:/^Track\b/}).selectOption('rust');await page.getByLabel('Accept terms',{exact:true}).check();
  const data=await page.getByRole('form',{name:'Workshop registration'}).evaluate(f=>Object.fromEntries(new FormData(f)));expect(data).toMatchObject({name:'Ada',email:'ada@example.com',tickets:'2',track:'rust'});expect(data).toHaveProperty('terms');
});
