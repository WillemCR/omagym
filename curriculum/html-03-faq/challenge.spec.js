import { test, expect } from '@playwright/test';

test.use({ javaScriptEnabled: false });
test.beforeEach(async ({ page }) => { await page.goto('/'); });

const answers=['Bring a laptop and curiosity.','Yes, all exercises run locally.','Finish at your own pace.'];
// Answer state without requiring a wrapper element. Whitespace is normalized and <br> counts as a space.
// text: the details' own content outside its summary; rendered: whether the answer is in the rendered text (innerText);
// visible: every non-empty answer text node has a box, non-zero effective opacity and visibility visible.
const answerState=d=>{const norm=t=>t.replace(/\s+/g,' ').trim();const copy=d.cloneNode(true);copy.querySelector(':scope > summary')?.remove();for(const br of copy.querySelectorAll('br'))br.replaceWith(' ');const summary=d.querySelector(':scope > summary');const walker=document.createTreeWalker(d,NodeFilter.SHOW_TEXT);let visible=true;for(let n=walker.nextNode();n;n=walker.nextNode()){if(!n.textContent.trim()||summary?.contains(n))continue;const range=document.createRange();range.selectNodeContents(n);let opacity=1;for(let e=n.parentElement;e;e=e.parentElement)opacity*=parseFloat(getComputedStyle(e).opacity);if(range.getClientRects().length===0||opacity===0||getComputedStyle(n.parentElement).visibility!=='visible')visible=false;}return {text:norm(copy.textContent),rendered:norm(d.innerText),visible};};
const state=(page,i)=>page.locator('details').nth(i).evaluate(answerState);
const expectShown=async(page,i,shown)=>{await expect.poll(async()=>{const s=await state(page,i);return shown?s.rendered.includes(answers[i])&&s.visible:!s.rendered.includes(answers[i]);},`answer ${i+1} ${shown?'visibly shown':'hidden'}`).toBe(true);};

test("FAQ begins with all answers collapsed", async ({ page }) => {
  const main=page.getByRole('main');await expect(main).toHaveCount(1);await expect(main.getByRole('heading',{name:'Weekend FAQ',level:1})).toBeVisible();await expect(main.locator('details')).toHaveCount(3);await expect(page.locator('details')).toHaveCount(3);await expect(page.locator('details[open]')).toHaveCount(0);await expect(page.locator('details > summary')).toHaveText(['What should I bring?','Can I join remotely?','Is there a deadline?']);
  for(const [i,answer] of answers.entries()){expect((await state(page,i)).text,`answer ${i+1} sits inside its details, outside the summary`).toContain(answer);await expectShown(page,i,false);}
});

test("FAQ pointer toggles independently", async ({ page }) => {
  const summaries=page.locator('details > summary');await summaries.nth(0).click();await expectShown(page,0,true);await summaries.nth(1).click();await expectShown(page,1,true);await expect(page.locator('details[open]')).toHaveCount(2);await summaries.nth(0).click();await expectShown(page,0,false);await expectShown(page,1,true);
});

test("FAQ supports native keyboard activation", async ({ page }) => {
  const summaries=page.locator('details > summary'),reached=new Set();
  for(let i=0;i<12&&reached.size<3;i++){await page.keyboard.press('Tab');for(let j=0;j<3;j++)if(await summaries.nth(j).evaluate(e=>e===document.activeElement))reached.add(j);}
  expect([...reached].sort((a,b)=>a-b),'every summary is reachable with Tab').toEqual([0,1,2]);
  await summaries.nth(2).focus();await page.keyboard.press('Enter');await expectShown(page,2,true);await page.keyboard.press('Space');await expectShown(page,2,false);
});
