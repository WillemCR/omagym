import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Utility card is centered at phone and desktop sizes", async ({ page }) => {
  for(const width of [390,1200]){await page.setViewportSize({width,height:800});const box=await page.locator('.profile').boundingBox();expect(Math.abs(box.width-320)).toBeLessThan(1);expect(Math.abs(box.x+box.width/2-width/2)).toBeLessThan(1);expect(Math.abs(box.y+box.height/2-400)).toBeLessThan(1);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);}
});

test("Utility card exposes spacing shape and type hierarchy", async ({ page }) => {
  const card=page.locator('.profile');await expect(card).toHaveCSS('padding','24px');await expect(card).toHaveCSS('border-radius','16px');expect(await card.evaluate(e=>getComputedStyle(e).boxShadow)).not.toBe('none');const avatar=await page.locator('.avatar').boundingBox();expect(avatar.width).toBe(64);expect(avatar.height).toBe(64);expect(await page.locator('.avatar').evaluate(e=>parseFloat(getComputedStyle(e).borderTopLeftRadius))).toBeGreaterThanOrEqual(32);await expect(page.getByRole('heading',{level:1})).toHaveCSS('font-size','24px');expect(await page.getByRole('heading',{level:1}).evaluate(e=>Number(getComputedStyle(e).fontWeight))).toBeGreaterThanOrEqual(600);
});

test("Utility card action has a generous full-width target", async ({ page }) => {
  const card=await page.locator('.profile').boundingBox(),link=await page.getByRole('link',{name:'View projects'}).boundingBox();expect(link.height).toBeGreaterThanOrEqual(44);expect(link.width).toBeCloseTo(card.width-48,0);await page.getByRole('link',{name:'View projects'}).click();await expect(page).toHaveURL(/#projects$/);
});
