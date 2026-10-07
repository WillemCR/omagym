import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

// Out of view, defined by what a user can perceive: no visible area inside the viewport, fully transparent,
// or not hit-testable anywhere on its box (clipped away, covered, visibility hidden). Hit-testing temporarily forces
// pointer-events:auto so a keyboard-only link with pointer-events:none is still judged by what is painted.
const visuallyHidden=e=>{const r=e.getBoundingClientRect(),x0=Math.max(r.left,0),x1=Math.min(r.right,innerWidth),y0=Math.max(r.top,0),y1=Math.min(r.bottom,innerHeight);if(x1-x0<=1||y1-y0<=1)return true;let opacity=1;for(let n=e;n;n=n.parentElement)opacity*=parseFloat(getComputedStyle(n).opacity);if(opacity===0)return true;const prior=[e.style.getPropertyValue('pointer-events'),e.style.getPropertyPriority('pointer-events')];e.style.setProperty('pointer-events','auto','important');let hidden=true;for(let i=1;i<=5&&hidden;i++)for(let j=1;j<=5;j++){const hit=document.elementFromPoint(x0+(x1-x0)*i/6,y0+(y1-y0)*j/6);if(hit&&(hit===e||e.contains(hit))){hidden=false;break;}}if(prior[0])e.style.setProperty('pointer-events',prior[0],prior[1]);else e.style.removeProperty('pointer-events');return hidden;};

test("Navigation rearranges between phone and desktop", async ({ page }) => {
  const links=page.getByRole('navigation',{name:'Main'}).getByRole('link');await page.setViewportSize({width:390,height:800});const a=await links.nth(0).boundingBox(),b=await links.nth(1).boundingBox();expect(b.y-a.y-a.height).toBeCloseTo(16,0);expect(Math.abs(a.x-b.x)).toBeLessThan(1);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.setViewportSize({width:1000,height:800});const c=await links.nth(0).boundingBox(),d=await links.nth(1).boundingBox();expect(Math.abs(c.y-d.y)).toBeLessThan(1);expect(d.x-c.x-c.width).toBeCloseTo(16,0);
});

test("Navigation highlights current and focused links", async ({ page }) => {
  const current=page.getByRole('link',{name:'Lessons',exact:true});await expect(current).toHaveCSS('background-color','rgb(30, 64, 175)');await expect(current).toHaveCSS('color','rgb(255, 255, 255)');await expect(current).toHaveCSS('border-radius','8px');await page.keyboard.press('Tab');
  for(const name of ['Overview','Lessons','Notes']){await page.keyboard.press('Tab');const link=page.getByRole('link',{name,exact:true});await expect(link).toBeFocused();await expect.poll(()=>link.evaluate(e=>e.getAnimations().filter(a=>a instanceof CSSTransition).length),'focus styles finish transitioning').toBe(0);const style=await link.evaluate(e=>{const s=getComputedStyle(e);return {outline:s.outlineStyle,width:parseFloat(s.outlineWidth),color:s.outlineColor,padding:Math.min(...['Top','Right','Bottom','Left'].map(side=>parseFloat(s['padding'+side])))}});expect(style.outline).toBe('solid');expect(style.width).toBeGreaterThanOrEqual(2);expect(style.color).not.toMatch(/^transparent$|^rgba\(.*,\s*0\)$|\/\s*0%?\s*\)$/);expect(style.padding).toBeGreaterThanOrEqual(12);}
});

test("Navigation skip link appears and transfers focus", async ({ page }) => {
  const skip=page.getByRole('link',{name:'Skip to content'});await expect.poll(()=>skip.evaluate(visuallyHidden),'skip link is out of view before focus').toBe(true);await page.keyboard.press('Tab');await expect(skip).toBeFocused();await expect.poll(()=>skip.evaluate(visuallyHidden),'focused skip link is visible').toBe(false);await expect.poll(()=>skip.evaluate(e=>{const r=e.getBoundingClientRect();return r.left>=0&&r.top>=0&&r.right<=innerWidth&&r.bottom<=innerHeight;}),'focused skip link settles fully inside the viewport').toBe(true);await page.keyboard.press('Enter');await expect(page.getByRole('main')).toBeFocused();
});
