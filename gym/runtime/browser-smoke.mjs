import { chromium } from '@playwright/test';
await import('./web-server.mjs');
const browser = await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
try {
 const page=await browser.newPage(); const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const response=await page.goto('http://127.0.0.1:4399/',{waitUntil:'networkidle',timeout:20000});
 if (!response?.ok()) errors.push('The app did not return a successful page.');
 if (!(await page.locator('body').innerText()).trim()) errors.push('The starter renders an empty page.');
 if (await page.locator('vite-error-overlay').count()) errors.push('Vite reported a compilation error.');
 if (errors.length) throw new Error(errors.join('\n'));
 console.log('OMAGYM_BROWSER_READY');
 await browser.close();process.exit(0);
} catch(e) {console.error(e.message);await browser.close();process.exit(1);}
