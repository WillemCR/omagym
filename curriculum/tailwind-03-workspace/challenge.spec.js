import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Utility workspace has a fixed desktop sidebar and flexible main", async ({ page }) => {
  await page.setViewportSize({width:1200,height:800});const aside=await page.locator('aside').boundingBox(),main=await page.locator('main').boundingBox(),shell=await page.locator('.shell').boundingBox();expect(aside.width).toBeCloseTo(240,0);expect(main.x).toBeCloseTo(aside.x+aside.width,0);expect(main.y).toBeCloseTo(aside.y,0);expect(main.width+aside.width).toBeCloseTo(shell.width,0);expect(shell.height).toBeGreaterThanOrEqual(800);
});

test("Utility workspace stacks on mobile without overflow", async ({ page }) => {
  await page.setViewportSize({width:390,height:800});const aside=await page.locator('aside').boundingBox(),main=await page.locator('main').boundingBox();expect(main.y).toBeGreaterThanOrEqual(aside.y+aside.height);expect(main.width).toBeCloseTo(aside.width,0);const a=await page.locator('.stats article').nth(0).boundingBox(),b=await page.locator('.stats article').nth(1).boundingBox();expect(a.x).toBeCloseTo(b.x,0);expect(b.y-a.y-a.height).toBeCloseTo(16,0);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test("Utility workspace statistics have consistent desktop spacing", async ({ page }) => {
  await page.setViewportSize({width:1200,height:800});const cards=page.locator('.stats article');await expect(cards).toHaveCount(3);const boxes=await Promise.all([0,1,2].map(i=>cards.nth(i).boundingBox()));expect(boxes[0].y).toBeCloseTo(boxes[2].y,0);expect(boxes[0].width).toBeCloseTo(boxes[2].width,0);expect(boxes[1].x-boxes[0].x-boxes[0].width).toBeCloseTo(16,0);await expect(page.locator('main')).toHaveCSS('padding','24px');await expect(cards.first()).toHaveCSS('padding','16px');await expect(cards.first()).toHaveCSS('border-radius','8px');expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
