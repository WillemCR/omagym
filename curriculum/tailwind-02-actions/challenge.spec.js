import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

// Duration that applies to background-color (the last matching entry or "all" wins, as in CSS), or null when it is not transitioned.
const backgroundDuration=e=>{const s=getComputedStyle(e),props=s.transitionProperty.split(',').map(x=>x.trim()),d=s.transitionDuration.split(',').map(x=>parseFloat(x)*(x.trim().endsWith('ms')?0.001:1));const i=props.findLastIndex(x=>x==='background-color'||x==='background'||x==='all');return i<0?null:d[i%d.length];};

test("Utility actions provide practical targets and disabled styling", async ({ page }) => {
  for(const id of ['save','locked']){const b=page.locator('#'+id),box=await b.boundingBox();expect(box.height).toBeGreaterThanOrEqual(44);await expect(b).toHaveCSS('border-radius','8px');const padding=await b.evaluate(e=>parseFloat(getComputedStyle(e).paddingLeft));expect(padding).toBeGreaterThanOrEqual(16);}
  await expect(page.locator('#locked')).toBeDisabled();await expect(page.locator('#locked')).toHaveCSS('opacity','0.5');await expect(page.locator('#locked')).toHaveCSS('cursor','not-allowed');
});

test("Utility action hover changes and restores its background", async ({ page }) => {
  await page.emulateMedia({reducedMotion:'reduce'});const b=page.locator('#save'),initial=await b.evaluate(e=>getComputedStyle(e).backgroundColor);expect(initial).not.toBe('rgba(0, 0, 0, 0)');await b.hover();await expect.poll(()=>b.evaluate(e=>getComputedStyle(e).backgroundColor)).not.toBe(initial);await page.getByRole('heading').hover();await expect.poll(()=>b.evaluate(e=>getComputedStyle(e).backgroundColor)).toBe(initial);
});

test("Utility action keyboard outline and motion preferences work", async ({ page }) => {
  await page.keyboard.press('Tab');const b=page.locator('#save');await expect(b).toBeFocused();await expect.poll(()=>b.evaluate(e=>e.getAnimations().filter(a=>a instanceof CSSTransition).length),'focus styles finish transitioning').toBe(0);const style=await b.evaluate(e=>{const s=getComputedStyle(e);return {kind:s.outlineStyle,width:parseFloat(s.outlineWidth),offset:parseFloat(s.outlineOffset),color:s.outlineColor}});expect(style.kind).toBe('solid');expect(style.color,'focus outline color is visible').not.toMatch(/^transparent$|^rgba\(.*,\s*0\)$|\/\s*0%?\s*\)$/);expect(style.width).toBeGreaterThanOrEqual(2);expect(style.offset).toBeGreaterThanOrEqual(2);await page.keyboard.press('Tab');await expect(page.locator('#locked')).not.toBeFocused();await page.emulateMedia({reducedMotion:'no-preference'});const d=await b.evaluate(backgroundDuration);expect(d,'background-color is transitioned').not.toBeNull();expect(d).toBeGreaterThan(0);await page.emulateMedia({reducedMotion:'reduce'});await expect.poll(()=>b.evaluate(e=>getComputedStyle(e).transitionDuration.split(',').every(x=>parseFloat(x)===0))).toBe(true);
});
