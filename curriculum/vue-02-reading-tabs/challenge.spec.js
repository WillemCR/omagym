import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Tabs start with one selected panel", async ({ page }) => {
  await expect(page.getByRole('tablist',{name:'Reading guide'})).toBeVisible();await expect(page.getByRole('tab')).toHaveCount(3);await expect(page.getByRole('tab',{name:'Overview',exact:true})).toHaveAttribute('aria-selected','true');await expect(page.getByRole('tabpanel',{name:'Overview',exact:true})).toHaveText('Welcome to Vue');await expect(page.getByRole('tabpanel')).toHaveCount(1);await expect(page.locator('[role="tab"][aria-selected="true"]')).toHaveCount(1);
});

test("Tabs respond to clicks and expose selection", async ({ page }) => {
  await page.getByRole('tab',{name:'Examples',exact:true}).click();await expect(page.getByRole('tabpanel',{name:'Examples',exact:true})).toHaveText('Practice makes progress');await expect(page.getByRole('tab',{name:'Examples',exact:true})).toHaveAttribute('aria-selected','true');await expect(page.getByRole('tab',{name:'Overview',exact:true})).toHaveAttribute('aria-selected','false');await expect(page.getByRole('tab',{name:'Overview',exact:true})).toHaveJSProperty('tabIndex',-1);await expect(page.getByRole('tab',{name:'Examples',exact:true})).toHaveJSProperty('tabIndex',0);
});

const panels={Overview:'Welcome to Vue',Examples:'Practice makes progress',Resources:'Read the official guide'};
async function expectActive(page,name){
  const tab=page.getByRole('tab',{name,exact:true});await expect(tab).toBeFocused();await expect(tab).toHaveAttribute('aria-selected','true');await expect(tab).toHaveJSProperty('tabIndex',0);
  for(const other of Object.keys(panels).filter(n=>n!==name)){const o=page.getByRole('tab',{name:other,exact:true});await expect(o).toHaveAttribute('aria-selected','false');await expect(o).toHaveJSProperty('tabIndex',-1);}
  await expect(page.getByRole('tabpanel')).toHaveCount(1);await expect(page.getByRole('tabpanel',{name,exact:true})).toHaveText(panels[name]);
}

test("Tabs keyboard wraps and supports home and end", async ({ page }) => {
  const overview=page.getByRole('tab',{name:'Overview',exact:true});await overview.focus();
  for(const [key,name] of [['ArrowLeft','Resources'],['ArrowRight','Overview'],['ArrowRight','Examples'],['ArrowRight','Resources'],['Home','Overview'],['End','Resources'],['ArrowLeft','Examples'],['Home','Overview']]){await page.keyboard.press(key);await expectActive(page,name);}
  await page.getByRole('tab',{name:'Examples',exact:true}).click();await expectActive(page,'Examples');await page.keyboard.press('ArrowRight');await expectActive(page,'Resources');
});
