/**
 * Automated demo recording for AI Phishing Detector.
 *
 * Prerequisites:
 *   - Backend running:  cd backend && uvicorn app.main:app --reload
 *   - Frontend running: cd frontend && npm run dev
 *   - Playwright installed: cd scripts && npm install
 *
 * Usage:
 *   cd scripts && node record-demo.js
 *
 * Output:
 *   scripts/video-out/<timestamp>.webm  — upload to YouTube
 *   docs/screenshots/phishing-result.png
 *   docs/screenshots/legit-result.png
 *   docs/screenshots/header-analysis.png
 */

import { chromium } from 'playwright'
import { mkdirSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const VIDEO_DIR = join(__dirname, 'video-out')
const SCREENSHOT_DIR = join(__dirname, '..', 'docs', 'screenshots')
mkdirSync(VIDEO_DIR, { recursive: true })
mkdirSync(SCREENSHOT_DIR, { recursive: true })

const FRONTEND_URL = 'http://localhost:5173'
const VIEWPORT = { width: 1280, height: 800 }

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

// Synthetic phishing headers that will trigger SPF fail + Reply-To mismatch
const PHISHING_HEADERS = `From: PayPal Security <security@paypal.com>
Reply-To: account-harvest@attacker-domain.example.com
Return-Path: <bounce@attacker-domain.example.com>
Authentication-Results: mx.google.com;
  spf=fail smtp.mailfrom=attacker-domain.example.com;
  dkim=fail header.d=paypal.com;
  dmarc=fail
Received: from attacker-server.example.com ([203.0.113.42])
  by mx.google.com with ESMTP
Date: Mon, 21 Apr 2026 19:00:00 +0000
MIME-Version: 1.0`

async function waitForMLResult(page) {
  await page.waitForSelector('.score-value', { timeout: 30000 })
}

async function waitForFullResults(page) {
  // Wait for ML score
  await page.waitForSelector('.score-value', { timeout: 30000 })
  // Wait for LLM card to resolve (reasoning shown, or disabled state if no API key)
  await page.waitForSelector('.reasoning, .disabled-text', { timeout: 45000 })
}

async function main() {
  const browser = await chromium.launch({ headless: false, slowMo: 110 })
  const context = await browser.newContext({
    viewport: VIEWPORT,
    recordVideo: { dir: VIDEO_DIR, size: VIEWPORT },
  })
  const page = await context.newPage()

  // ── 1. App load ─────────────────────────────────────────────────────────────
  console.log('Opening app...')
  await page.goto(FRONTEND_URL)
  await page.waitForSelector('.sample-btn', { timeout: 10000 })
  console.log('App loaded.')
  await sleep(3000) // let the viewer read the UI

  // ── 2. Phishing sample — ML + LLM + IOC extraction ──────────────────────────
  console.log('\nScene 1: Phishing email — ML + LLM analysis')
  await page.locator('.sample-btn--phishing').first().click()
  await sleep(1200) // show the email loaded into the form

  await page.getByRole('button', { name: 'Analyze' }).click()
  console.log('  Waiting for results...')
  await waitForFullResults(page)
  console.log('  Results rendered.')
  await sleep(3000) // linger on ML score + risk badge + LLM reasoning

  // Scroll down slowly to reveal IOCs and feature weights
  await page.evaluate(() => window.scrollBy({ top: 250, behavior: 'smooth' }))
  await sleep(4000) // linger on IOC list and top signals

  await page.screenshot({ path: join(SCREENSHOT_DIR, 'phishing-result.png'), fullPage: false })
  console.log('  Screenshot: phishing-result.png')

  // Scroll back to top
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }))
  await sleep(1500)

  // ── 3. Header analysis — expand toggle, paste phishing headers ──────────────
  console.log('\nScene 2: Header analysis — SPF/DKIM/DMARC + domain mismatch')

  // Open the headers <details> toggle slowly so the viewer sees it
  await page.locator('.headers-toggle summary').click()
  await sleep(1200)

  // Type headers gradually so the viewer can read what's being pasted
  await page.fill('#headers', PHISHING_HEADERS)
  await sleep(1500)

  // Scroll so the form + analyze button are both visible
  await page.evaluate(() => window.scrollBy({ top: 120, behavior: 'smooth' }))
  await sleep(800)

  await page.getByRole('button', { name: 'Analyze' }).click()
  console.log('  Waiting for results with header analysis...')
  await waitForFullResults(page)

  // Wait for the Header Analysis card (auth row appears when headers processed)
  await page.waitForSelector('.auth-row', { timeout: 15000 })
  console.log('  Header analysis card rendered.')
  await sleep(2000)

  // Scroll down to reveal the full Header Analysis card
  await page.evaluate(() => window.scrollBy({ top: 600, behavior: 'smooth' }))
  await sleep(5000) // linger on SPF/DKIM/DMARC badges + domain chain + flags

  await page.screenshot({ path: join(SCREENSHOT_DIR, 'header-analysis.png'), fullPage: false })
  console.log('  Screenshot: header-analysis.png')

  // Scroll back to top
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }))
  await sleep(1500)

  // ── 4. Legitimate email — false positive check ──────────────────────────────
  console.log('\nScene 3: Legitimate email — false positive check')

  // Clear headers while panel is still open, then close it
  await page.fill('#headers', '')
  await sleep(400)
  await page.locator('.headers-toggle summary').click()
  await sleep(700)

  await page.locator('.sample-btn--legit').first().click()
  await sleep(1200) // show the legit email loaded

  await page.getByRole('button', { name: 'Analyze' }).click()
  console.log('  Waiting for legit results...')
  await waitForFullResults(page)
  console.log('  Legit results rendered.')
  await sleep(4000) // linger on low-risk verdict

  await page.screenshot({ path: join(SCREENSHOT_DIR, 'legit-result.png'), fullPage: false })
  console.log('  Screenshot: legit-result.png')

  // Final pause — let the full 3-card layout sit on screen
  await sleep(3000)

  await context.close()
  await browser.close()

  console.log('\n✓ Done.')
  console.log(`  Video      → ${VIDEO_DIR}/`)
  console.log(`  Screenshots → ${SCREENSHOT_DIR}/`)
  console.log('\nNext steps:')
  console.log('  1. Upload the .webm from video-out/ to YouTube as unlisted')
  console.log('  2. Copy the YouTube URL into README.md (replace the [Watch Demo Video →] link)')
  console.log('  3. Commit the new screenshots: git add docs/screenshots/ && git commit')
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})
