#!/usr/bin/env node
/**
 * Renders the three cover images CrazyGames asks for at submission.
 *
 *   node tools/make-covers.mjs        (or: npm run covers)
 *
 * The composition lives in tools/cover.html — edit that, re-run this. Output
 * lands in release/covers/. Sizes come straight from the portal's spec
 * (docs.crazygames.com/requirements/game-covers):
 *
 *   landscape  1920x1080  16:9
 *   portrait    800x1200  2:3
 *   square       800x800  1:1
 */
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const TEMPLATE = path.join(ROOT, 'tools', 'cover.html');
const OUT = path.join(ROOT, 'release', 'covers');

const FORMATS = [
  { name: 'landscape', w: 1920, h: 1080 },
  { name: 'portrait',  w: 800,  h: 1200 },
  { name: 'square',    w: 800,  h: 800  }
];

// Headless Chrome is the renderer. No other browser is assumed to be here, so
// say plainly which one is missing rather than failing on a spawn error.
const CHROME_CANDIDATES = [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser'
];
const chrome = process.env.CHROME_PATH || CHROME_CANDIDATES.find((p) => fs.existsSync(p));
if (!chrome) {
  console.error('Could not find Chrome. Install it, or set CHROME_PATH to the binary.');
  process.exit(1);
}

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });

for (const { name, w, h } of FORMATS) {
  const file = path.join(OUT, `sumi-${name}-${w}x${h}.png`);
  execFileSync(chrome, [
    '--headless=new',
    '--disable-gpu',
    '--hide-scrollbars',
    // The page reads sprite sheets out of public/assets over file://
    '--allow-file-access-from-files',
    '--force-device-scale-factor=1',
    `--window-size=${w},${h}`,
    '--virtual-time-budget=4000',
    `--screenshot=${file}`,
    `file://${TEMPLATE}?format=${name}`
  ], { stdio: ['ignore', 'ignore', 'ignore'] });

  if (!fs.existsSync(file)) {
    console.error(`✗ ${name}: Chrome wrote nothing`);
    process.exit(1);
  }
  // A window narrower than Chrome's minimum silently lays out wider than
  // asked, so the only trustworthy check is the file that came out.
  const { width, height } = readPngSize(file);
  const ok = width === w && height === h;
  console.log(`${ok ? '✓' : '✗'} ${name.padEnd(9)} ${width}x${height}` +
              (ok ? '' : `  — expected ${w}x${h}`) +
              `  ${(fs.statSync(file).size / 1024).toFixed(0)} KB`);
  if (!ok) process.exit(1);
}

console.log('\n→ ' + path.relative(ROOT, OUT));

/** Reads width/height out of a PNG's IHDR, which is always the first chunk. */
function readPngSize(file) {
  const buf = fs.readFileSync(file, { length: 33 });
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}
