import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

// True when at least one shadow layer has a non-transparent color and a nonzero offset, blur or spread.
const visibleShadow=e=>{const v=getComputedStyle(e).boxShadow;if(v==='none')return false;const alpha=c=>{if(!c||c==='transparent')return 0;const slash=c.match(/\/\s*([\d.]+)(%?)\s*\)$/);if(slash)return parseFloat(slash[1])/(slash[2]?100:1);const parts=c.slice(c.indexOf('(')+1,-1).split(',');return parts.length===4?parseFloat(parts[3]):1;};return v.split(/,(?![^(]*\))/).some(layer=>{const color=layer.match(/[a-z-]+\([^)]*\)|transparent/)?.[0]??'';const lengths=layer.replace(color,'').match(/-?[\d.]+px/g)??[];return alpha(color)>0&&lengths.some(x=>parseFloat(x)!==0);});};

// Circular when every corner radius is at least half the 64px side, or a circle clip-path of at least that radius is applied.
const roundShape=e=>{const s=getComputedStyle(e);if(['TopLeft','TopRight','BottomRight','BottomLeft'].every(c=>parseFloat(s[`border${c}Radius`])>=32||s[`border${c}Radius`].endsWith('%')&&parseFloat(s[`border${c}Radius`])>=50))return true;const clip=s.clipPath;if(!clip.startsWith('circle('))return false;const m=clip.match(/^circle\(([\d.]+)(px|%)/);return !m||(m[2]==='%'?parseFloat(m[1])>=50:parseFloat(m[1])>=32);};

test("Utility card is centered at phone and desktop sizes", async ({ page }) => {
  for(const width of [390,1200]){await page.setViewportSize({width,height:800});const box=await page.locator('.profile').boundingBox();expect(Math.abs(box.width-320)).toBeLessThan(1);expect(Math.abs(box.x+box.width/2-width/2)).toBeLessThan(1);expect(Math.abs(box.y+box.height/2-400)).toBeLessThan(1);const main=await page.locator('main').boundingBox();expect(main.height).toBeGreaterThanOrEqual(800);expect(Math.abs(box.x+box.width/2-(main.x+main.width/2))).toBeLessThan(1);expect(Math.abs(box.y+box.height/2-(main.y+main.height/2))).toBeLessThan(1);expect(await page.locator('.profile').evaluate(e=>e.closest('main')!==null)).toBe(true);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);}
});

test("Utility card exposes spacing shape and type hierarchy", async ({ page }) => {
  const card=page.locator('.profile');await expect(card).toHaveCSS('padding','24px');await expect(card).toHaveCSS('border-radius','16px');expect(await card.evaluate(visibleShadow),'card has a visible box shadow').toBe(true);const avatar=await page.locator('.avatar').boundingBox();expect(avatar.width).toBe(64);expect(avatar.height).toBe(64);expect(await page.locator('.avatar').evaluate(roundShape),'avatar renders as a circle').toBe(true);await expect(page.getByRole('heading',{level:1})).toHaveCSS('font-size','24px');expect(await page.getByRole('heading',{level:1}).evaluate(e=>Number(getComputedStyle(e).fontWeight))).toBeGreaterThanOrEqual(600);
});

test("Utility card action has a generous full-width target", async ({ page }) => {
  const link=await page.getByRole('link',{name:'View projects'}).boundingBox();expect(link.height).toBeGreaterThanOrEqual(44);const content=await page.locator('.profile').evaluate(e=>{const s=getComputedStyle(e);return e.clientWidth-parseFloat(s.paddingLeft)-parseFloat(s.paddingRight);});expect(link.width).toBeCloseTo(content,0);await page.getByRole('link',{name:'View projects'}).click();await expect(page).toHaveURL(/#projects$/);
});
