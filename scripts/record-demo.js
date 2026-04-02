import { chromium } from 'playwright'
import { mkdirSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const VIDEO_DIR = join(__dirname, 'video-out')
const SCREENSHOT_DIR = join(__dirname, 'screenshots')
mkdirSync(VIDEO_DIR, { recursive: true })
mkdirSync(SCREENSHOT_DIR, { recursive: true })

const FRONTEND_URL = 'http://localhost:5173'
const VIEWPORT = { width: 1280, height: 800 }

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

async function waitForResults(page) {
  await page.waitForSelector('.score-value', { timeout: 30000 })
  // LLM result renders as reasoning text, loading indicator, or disabled state
  await page.waitForSelector('.reasoning, .disabled-text', { timeout: 45000 })
}

async function main() {
  const browser = await chromium.launch({ headless: false })
  const context = await browser.newContext({
    viewport: VIEWPORT,
    recordVideo: { dir: VIDEO_DIR, size: VIEWPORT },
  })
  const page = await context.newPage()

  console.log('Opening app at', FRONTEND_URL)
  await page.goto(FRONTEND_URL)

  // Wait for sample buttons to appear (confirms /api/samples responded)
  await page.waitForSelector('.sample-btn', { timeout: 10000 })
  console.log('App loaded, samples visible.')
  await sleep(1500)

  // ── Phishing sample ────────────────────────────────────────────────────────
  console.log('Clicking first phishing sample...')
  await page.locator('.sample-btn--phishing').first().click()
  await sleep(600)

  console.log('Clicking Analyze...')
  await page.getByRole('button', { name: 'Analyze' }).click()

  console.log('Waiting for phishing results...')
  await waitForResults(page)
  console.log('Phishing results rendered.')
  await sleep(3500)

  // Screenshot for README
  await page.screenshot({ path: join(SCREENSHOT_DIR, 'phishing-result.png'), fullPage: false })
  console.log('Screenshot saved: phishing-result.png')

  // ── Legit sample ───────────────────────────────────────────────────────────
  console.log('Clicking first legit sample...')
  await page.locator('.sample-btn--legit').first().click()
  await sleep(600)

  console.log('Clicking Analyze...')
  await page.getByRole('button', { name: 'Analyze' }).click()

  console.log('Waiting for legit results...')
  await waitForResults(page)
  console.log('Legit results rendered.')
  await sleep(3500)

  // Screenshot for README
  await page.screenshot({ path: join(SCREENSHOT_DIR, 'legit-result.png'), fullPage: false })
  console.log('Screenshot saved: legit-result.png')

  await context.close()
  await browser.close()

  console.log('\n✓ Done.')
  console.log(`  Video  → ${VIDEO_DIR}`)
  console.log(`  Screenshots → ${SCREENSHOT_DIR}`)
  console.log('\nNext steps:')
  console.log('  1. Upload the .webm from video-out/ to https://www.loom.com/upload')
  console.log('  2. Copy the Loom share URL into README.md (search for LOOM_URL_HERE)')
  console.log('  3. Copy screenshots to docs/screenshots/ and commit them')
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})
