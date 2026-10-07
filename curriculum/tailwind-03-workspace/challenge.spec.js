import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Utility workspace has a fixed desktop sidebar and flexible main", async ({ page }) => {
  await page.setViewportSize({width:1200,height:800});const aside=await page.locator('aside').boundingBox(),main=await page.locator('main').boundingBox(),shell=await page.locator('.shell').boundingBox();expect(aside.width).toBeCloseTo(240,0);expect(main.x).toBeCloseTo(aside.x+aside.width,0);expect(main.y).toBeCloseTo(aside.y,0);expect(main.width+aside.width).toBeCloseTo(shell.width,0);expect(shell.height).toBeGreaterThanOrEqual(800);
});

test("Utility workspace stacks on mobile without overflow", async ({ page }) => {
  await page.setViewportSize({width:390,height:800});const aside=await page.locator('aside').boundingBox(),main=await page.locator('main').boundingBox(),shell=await page.locator('.shell').boundingBox();expect(main.y).toBeGreaterThanOrEqual(aside.y+aside.height);for(const box of [aside,main]){expect(box.x).toBeCloseTo(0,0);expect(box.width).toBeCloseTo(390,0);}expect(shell.height).toBeGreaterThanOrEqual(800);
  const cards=page.locator('.stats article');await expect(cards).toHaveCount(3);const boxes=await Promise.all([0,1,2].map(i=>cards.nth(i).boundingBox()));for(const i of [0,1,2]){await expect(cards.nth(i)).toBeVisible();expect(boxes[i].x).toBeCloseTo(main.x+24,0);expect(boxes[i].width).toBeCloseTo(main.width-48,0);if(i)expect(boxes[i].y-boxes[i-1].y-boxes[i-1].height).toBeCloseTo(16,0);}expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test("Utility workspace statistics have consistent desktop spacing", async ({ page }) => {
  await page.setViewportSize({width:1200,height:800});const cards=page.locator('.stats article');await expect(cards).toHaveCount(3);const boxes=await Promise.all([0,1,2].map(i=>cards.nth(i).boundingBox()));const main=await page.locator('main').boundingBox();for(const i of [1,2]){expect(boxes[i].y).toBeCloseTo(boxes[0].y,0);expect(boxes[i].width).toBeCloseTo(boxes[0].width,0);expect(boxes[i].x-boxes[i-1].x-boxes[i-1].width).toBeCloseTo(16,0);}expect(boxes[0].x).toBeCloseTo(main.x+24,0);expect(boxes[2].x+boxes[2].width).toBeCloseTo(main.x+main.width-24,0);await expect(page.locator('main')).toHaveCSS('padding','24px');for(const card of await cards.all()){await expect(card).toHaveCSS('padding','16px');await expect(card).toHaveCSS('border-radius','8px');}expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
