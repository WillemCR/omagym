import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

const cardBoxes=page=>Promise.all([0,1,2].map(i=>page.locator('.card').nth(i).boundingBox()));

test("Gallery stacks comfortably on phones", async ({ page }) => {
  await page.setViewportSize({width:390,height:900});const cards=page.locator('.card');await expect(cards).toHaveCount(3);const boxes=await cardBoxes(page);
  for(const i of [1,2]){expect(Math.abs(boxes[i].x-boxes[0].x)).toBeLessThan(1);expect(Math.abs(boxes[i].width-boxes[0].width)).toBeLessThan(1);expect(boxes[i].y-boxes[i-1].y-boxes[i-1].height).toBeCloseTo(24,0);}
  expect(boxes[0].width).toBeGreaterThan(300);expect(boxes[0].x).toBeGreaterThanOrEqual(16);expect(390-boxes[0].x-boxes[0].width).toBeGreaterThanOrEqual(16);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test("Gallery uses three equal desktop columns", async ({ page }) => {
  for(const width of [900,1200]){await page.setViewportSize({width,height:900});const boxes=await cardBoxes(page);for(const i of [1,2]){expect(Math.abs(boxes[0].y-boxes[i].y)).toBeLessThan(1);expect(Math.abs(boxes[0].width-boxes[i].width)).toBeLessThan(1);expect(boxes[i].x-boxes[i-1].x-boxes[i-1].width).toBeCloseTo(24,0);}expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);}
});

test("Gallery cards and container meet spacing contract", async ({ page }) => {
  await page.setViewportSize({width:1200,height:900});for(const card of await page.locator('.card').all()){await expect(card).toHaveCSS('padding','24px');await expect(card).toHaveCSS('border-radius','12px');expect(await card.evaluate(e=>{const s=getComputedStyle(e);return s.backgroundColor!=='rgba(0, 0, 0, 0)'||s.backgroundImage!=='none';}),'card has a visible background').toBe(true);}const main=await page.locator('main').boundingBox();expect(main.width).toBeLessThanOrEqual(1100);expect(main.x).toBeGreaterThanOrEqual(16);expect(Math.abs(main.x-(1200-main.x-main.width))).toBeLessThan(1);
});
