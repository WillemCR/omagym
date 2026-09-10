import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test("Pricing aligns equal cards and bottom actions", async ({ page }) => {
  await page.setViewportSize({width:1000,height:900});const cards=await Promise.all([0,1].map(i=>page.locator('.plan').nth(i).boundingBox()));expect(Math.abs(cards[0].y-cards[1].y)).toBeLessThan(1);expect(Math.abs(cards[0].height-cards[1].height)).toBeLessThan(1);expect(Math.abs(cards[0].width-cards[1].width)).toBeLessThan(1);const links=await Promise.all([0,1].map(i=>page.locator('.plan a').nth(i).boundingBox()));expect(Math.abs(links[0].y+links[0].height-links[1].y-links[1].height)).toBeLessThanOrEqual(3);expect(links[0].height).toBeGreaterThanOrEqual(44);await expect(page.locator('.plan').first()).toHaveCSS('padding','24px');
});

test("Pricing stacks and grows with content", async ({ page }) => {
  await page.setViewportSize({width:390,height:900});const first=await page.locator('.plan').first().boundingBox(),second=await page.locator('.plan').nth(1).boundingBox();expect(second.y).toBeGreaterThanOrEqual(first.y+first.height);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.locator('.plan').first().evaluate(e=>{const p=document.createElement('p');p.textContent='More learning opportunities. '.repeat(100);e.insertBefore(p,e.lastElementChild)});const grown=await page.locator('.plan').first().boundingBox();expect(grown.height).toBeGreaterThan(first.height+100);
});

test("Pricing emphasizes Club and respects reduced motion", async ({ page }) => {
  const club=page.locator('.featured');await expect(club).toHaveCSS('border-top-width','3px');await expect(club).toHaveCSS('border-top-style','solid');await expect(club).toHaveCSS('border-top-color','rgb(30, 64, 175)');const link=page.locator('.plan a').first();await page.emulateMedia({reducedMotion:'no-preference'});expect(await link.evaluate(e=>getComputedStyle(e).transitionProperty.split(',').map(x=>x.trim()).some(x=>x==='transform'||x==='all'))).toBe(true);expect(await link.evaluate(e=>parseFloat(getComputedStyle(e).transitionDuration))).toBeGreaterThan(0);await page.emulateMedia({reducedMotion:'reduce'});await expect(link).toHaveCSS('transition-duration','0s');
});
