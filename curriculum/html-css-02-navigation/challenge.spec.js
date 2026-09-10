import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Navigation rearranges between phone and desktop", async ({ page }) => {
  const links=page.getByRole('navigation',{name:'Main'}).getByRole('link');await page.setViewportSize({width:390,height:800});const a=await links.nth(0).boundingBox(),b=await links.nth(1).boundingBox();expect(b.y-a.y-a.height).toBeCloseTo(16,0);expect(Math.abs(a.x-b.x)).toBeLessThan(1);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.setViewportSize({width:1000,height:800});const c=await links.nth(0).boundingBox(),d=await links.nth(1).boundingBox();expect(Math.abs(c.y-d.y)).toBeLessThan(1);expect(d.x-c.x-c.width).toBeCloseTo(16,0);
});

test("Navigation highlights current and focused links", async ({ page }) => {
  const current=page.getByRole('link',{name:'Lessons',exact:true});await expect(current).toHaveCSS('background-color','rgb(30, 64, 175)');await expect(current).toHaveCSS('color','rgb(255, 255, 255)');await expect(current).toHaveCSS('border-radius','8px');await page.keyboard.press('Tab');await page.keyboard.press('Tab');const first=page.getByRole('link',{name:'Overview',exact:true});await expect(first).toBeFocused();const style=await first.evaluate(e=>{const s=getComputedStyle(e);return {outline:s.outlineStyle,width:parseFloat(s.outlineWidth),padding:parseFloat(s.paddingTop)}});expect(style.outline).toBe('solid');expect(style.width).toBeGreaterThanOrEqual(2);expect(style.padding).toBeGreaterThanOrEqual(12);
});

test("Navigation skip link appears and transfers focus", async ({ page }) => {
  const skip=page.getByRole('link',{name:'Skip to content'});const hidden=await skip.boundingBox();expect(!hidden||hidden.y+hidden.height<=0||hidden.x+hidden.width<=0).toBe(true);await page.keyboard.press('Tab');await expect(skip).toBeFocused();const box=await skip.boundingBox();expect(box.x).toBeGreaterThanOrEqual(0);expect(box.y).toBeGreaterThanOrEqual(0);await page.keyboard.press('Enter');await expect(page.getByRole('main')).toBeFocused();
});
