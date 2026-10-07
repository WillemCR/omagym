import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => { await page.goto('/'); });

// Each named Choose link sits below every other card child and ends at the card's content-box bottom.
const actionAtBottom=a=>{const card=a.closest('.plan'),s=getComputedStyle(card),r=card.getBoundingClientRect(),l=a.getBoundingClientRect();const content=r.bottom-parseFloat(s.paddingBottom)-parseFloat(s.borderBottomWidth);const others=[...card.children].filter(c=>c!==a&&!c.contains(a)).map(c=>c.getBoundingClientRect().bottom);return {below:others.every(b=>l.top>=b-1),gap:content-l.bottom-parseFloat(getComputedStyle(a).marginBottom)};};
const transformDuration=e=>{const s=getComputedStyle(e),props=s.transitionProperty.split(',').map(x=>x.trim()),d=s.transitionDuration.split(',').map(x=>parseFloat(x)*(x.trim().endsWith('ms')?0.001:1));const i=props.findLastIndex(x=>x==='transform'||x==='all');return i<0?null:d[i%d.length];};

const chooseLinks=page=>page.locator('.plan').getByRole('link',{name:/^Choose\b/});
async function expectBottomActions(page){await expect(chooseLinks(page)).toHaveCount(2);for(const link of await chooseLinks(page).all()){const r=await link.evaluate(actionAtBottom);expect(r.below,'Choose link sits below the card content').toBe(true);expect(Math.abs(r.gap),'Choose link ends at the card bottom').toBeLessThanOrEqual(2);}}

test("Pricing aligns equal cards and bottom actions", async ({ page }) => {
  await page.setViewportSize({width:1000,height:900});const cards=await Promise.all([0,1].map(i=>page.locator('.plan').nth(i).boundingBox()));expect(Math.abs(cards[0].y-cards[1].y)).toBeLessThan(1);expect(Math.abs(cards[0].height-cards[1].height)).toBeLessThan(1);expect(Math.abs(cards[0].width-cards[1].width)).toBeLessThan(1);const links=await Promise.all([0,1].map(i=>chooseLinks(page).nth(i).boundingBox()));expect(Math.abs(links[0].y+links[0].height-links[1].y-links[1].height)).toBeLessThanOrEqual(3);for(const l of links)expect(l.height).toBeGreaterThanOrEqual(44);await expectBottomActions(page);for(const card of await page.locator('.plan').all())await expect(card).toHaveCSS('padding','24px');
});

test("Pricing stacks and grows with content", async ({ page }) => {
  await page.setViewportSize({width:390,height:900});const first=await page.locator('.plan').first().boundingBox(),second=await page.locator('.plan').nth(1).boundingBox();expect(second.y).toBeGreaterThanOrEqual(first.y+first.height);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await expectBottomActions(page);await page.locator('.plan').first().evaluate(e=>{const p=document.createElement('p');p.textContent='More learning opportunities. '.repeat(100);e.insertBefore(p,e.lastElementChild)});const grown=await page.locator('.plan').first().boundingBox();expect(grown.height).toBeGreaterThan(first.height+100);await expectBottomActions(page);
  await page.setViewportSize({width:1000,height:900});const before=await page.locator('.plan').nth(1).boundingBox();await page.locator('.plan').nth(1).evaluate(e=>{const p=document.createElement('p');p.textContent='Even more shared reviews. '.repeat(150);e.insertBefore(p,e.lastElementChild)});const after=await Promise.all([0,1].map(i=>page.locator('.plan').nth(i).boundingBox()));expect(after[1].height).toBeGreaterThan(before.height+100);expect(Math.abs(after[0].height-after[1].height)).toBeLessThan(1);await expectBottomActions(page);
});

test("Pricing emphasizes Club and respects reduced motion", async ({ page }) => {
  const club=page.locator('.plan').filter({has:page.getByRole('heading',{name:'Club',exact:true})});await expect(club).toHaveCount(1);await expect(club).toHaveCSS('border-top-width','3px');await expect(club).toHaveCSS('border-top-style','solid');await expect(club).toHaveCSS('border-top-color','rgb(30, 64, 175)');await page.emulateMedia({reducedMotion:'no-preference'});
  for(const link of await chooseLinks(page).all()){const d=await link.evaluate(transformDuration);expect(d,'a transform transition is declared').not.toBeNull();expect(d).toBeGreaterThan(0);}
  await page.emulateMedia({reducedMotion:'reduce'});for(const link of await chooseLinks(page).all())await expect.poll(()=>link.evaluate(e=>getComputedStyle(e).transitionDuration.split(',').every(x=>parseFloat(x)===0))).toBe(true);
});
