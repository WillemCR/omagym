import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Gallery stacks comfortably on phones", async ({ page }) => {
  await page.setViewportSize({width:390,height:900});const cards=page.locator('.card');await expect(cards).toHaveCount(3);const a=await cards.nth(0).boundingBox(),b=await cards.nth(1).boundingBox();expect(Math.abs(a.x-b.x)).toBeLessThan(1);expect(b.y-a.y-a.height).toBeCloseTo(24,0);expect(a.width).toBeGreaterThan(300);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test("Gallery uses three equal desktop columns", async ({ page }) => {
  for(const width of [900,1200]){await page.setViewportSize({width,height:900});const boxes=await Promise.all([0,1,2].map(i=>page.locator('.card').nth(i).boundingBox()));expect(Math.abs(boxes[0].y-boxes[2].y)).toBeLessThan(1);expect(Math.abs(boxes[0].width-boxes[2].width)).toBeLessThan(1);expect(boxes[1].x-boxes[0].x-boxes[0].width).toBeCloseTo(24,0);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);}
});

test("Gallery cards and container meet spacing contract", async ({ page }) => {
  await page.setViewportSize({width:1200,height:900});await expect(page.locator('.card').first()).toHaveCSS('padding','24px');await expect(page.locator('.card').first()).toHaveCSS('border-radius','12px');expect(await page.locator('.card').first().evaluate(e=>getComputedStyle(e).backgroundColor)).not.toBe('rgba(0, 0, 0, 0)');const main=await page.locator('main').boundingBox();expect(main.width).toBeLessThanOrEqual(1100);expect(main.x).toBeGreaterThanOrEqual(16);expect(Math.abs(main.x-(1200-main.x-main.width))).toBeLessThan(1);
});
