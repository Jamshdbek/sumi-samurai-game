#!/usr/bin/env node
/**
 * Builds the CrazyGames upload bundle.
 *
 *   node tools/package-crazygames.mjs        (or: npm run package)
 *
 * Produces `release/sumi-crazygames.zip` with index.html at the root of the
 * archive, which is what the developer portal expects. Along the way it drops
 * art that nothing in the game references and checks the bundle against the
 * portal's technical limits, so a rejection is caught here rather than after
 * an upload.
 *
 * Limits enforced (docs.crazygames.com/requirements/technical):
 *   - 250 MB total, 1500 files
 *   - 50 MB initial download (20 MB to be eligible for the mobile home page)
 *   - relative paths only; absolute paths fail to load on their CDN
 */
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIST = path.join(ROOT, 'dist');
const RELEASE = path.join(ROOT, 'release');
const ZIP_NAME = 'sumi-crazygames.zip';

// The one external request the portal allows — and requires
const SDK_HOST = 'sdk.crazygames.com';

const MB = 1024 * 1024;
const LIMITS = { total: 250 * MB, files: 1500, initial: 50 * MB, mobileInitial: 20 * MB };

const problems = [];
const notes = [];

const walk = (dir) => fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
  const full = path.join(dir, e.name);
  return e.isDirectory() ? walk(full) : [full];
});

const human = (n) => (n < MB ? (n / 1024).toFixed(0) + ' KB' : (n / MB).toFixed(2) + ' MB');

// ---------------------------------------------------------------- 1. build
console.log('▸ Building…');
execFileSync('npm', ['run', 'build'], { cwd: ROOT, stdio: 'inherit' });

const html = fs.readFileSync(path.join(DIST, 'index.html'), 'utf8');

// ------------------------------------------------- 2. drop unreferenced art
// The repo keeps source sheets and retired art next to the live art. Matching
// on basename is deliberately loose: a file survives if its name appears
// anywhere in the built HTML, so a path assembled at runtime still counts.
console.log('▸ Pruning unreferenced assets…');
let pruned = 0;
let prunedBytes = 0;
for (const file of walk(DIST)) {
  const rel = path.relative(DIST, file);
  if (rel === 'index.html') continue;
  const base = path.basename(file);
  // Dotfiles never belong in an upload
  if (base.startsWith('.') || !html.includes(base)) {
    prunedBytes += fs.statSync(file).size;
    fs.rmSync(file);
    pruned++;
    notes.push('pruned ' + rel);
  }
}
// Sweep up directories the prune emptied
for (let pass = 0; pass < 4; pass++) {
  for (const dir of walk(DIST).map((f) => path.dirname(f))) void dir;
  const emptyDirs = [];
  const scan = (dir) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      if (!e.isDirectory()) continue;
      const full = path.join(dir, e.name);
      scan(full);
      if (fs.readdirSync(full).length === 0) emptyDirs.push(full);
    }
  };
  scan(DIST);
  if (!emptyDirs.length) break;
  emptyDirs.forEach((d) => fs.rmdirSync(d));
}
console.log(`  removed ${pruned} file(s), ${human(prunedBytes)}`);

// ------------------------------------------------------------- 3. validate
console.log('▸ Checking the bundle…');

// Absolute asset paths break on their CDN, which serves the game from a
// nested directory rather than a domain root.
for (const m of html.matchAll(/(?:src|href)="(\/[^/][^"]*)"/g)) {
  problems.push(`absolute path in index.html: ${m[1]}`);
}

// Every remote resource except the SDK can stall the game behind a third
// party the portal does not control. Only things the browser actually
// fetches count — a plain <a href> to another site is a link, not a request,
// so anchors are left alone.
const remote = new Set();
const fetched = [...html.matchAll(/\ssrc="(https?:\/\/[^"]+)"/g),
                 ...html.matchAll(/<link\b[^>]*\shref="(https?:\/\/[^"]+)"/g)];
for (const m of fetched) {
  const host = new URL(m[1]).host;
  if (host !== SDK_HOST) remote.add(m[1]);
}
remote.forEach((u) => problems.push(`external request that is not the SDK: ${u}`));
if (!html.includes(SDK_HOST)) problems.push('the CrazyGames SDK script tag is missing');

// The SDK calls the portal checks for during review
for (const call of ['gameplayStart', 'gameplayStop', 'loadingStart', 'loadingStop']) {
  if (!html.includes(call)) problems.push(`SDK call missing: ${call}`);
}

const files = walk(DIST);
const total = files.reduce((n, f) => n + fs.statSync(f).size, 0);
if (total > LIMITS.total) problems.push(`bundle is ${human(total)}, over the ${human(LIMITS.total)} cap`);
if (files.length > LIMITS.files) problems.push(`${files.length} files, over the ${LIMITS.files} cap`);

// Everything ships up front: the splash preloads all of ART before Play is
// live, so the initial download is the whole bundle.
if (total > LIMITS.initial) problems.push(`initial download ${human(total)} exceeds ${human(LIMITS.initial)}`);
else if (total > LIMITS.mobileInitial) {
  notes.push(`initial download ${human(total)} is over ${human(LIMITS.mobileInitial)} — ` +
             'the game still passes, but it will not be eligible for the mobile home page');
}

// ----------------------------------------------------------------- 4. zip
// Only the zip is ours to replace — release/covers belongs to make-covers.mjs
fs.mkdirSync(RELEASE, { recursive: true });
const zipPath = path.join(RELEASE, ZIP_NAME);
fs.rmSync(zipPath, { force: true });
// -X drops the macOS resource forks that otherwise inflate the file count
execFileSync('zip', ['-r', '-q', '-X', zipPath, '.', '-x', '.*', '-x', '__MACOSX/*'], { cwd: DIST });

// Read the archive back rather than trusting that it holds what we meant.
// Zipping the project folder by hand instead of running this produces an
// archive whose index.html loads and whose art all 404s — the game comes up
// drawn entirely in fallback rectangles — so the layout is worth asserting.
const listing = execFileSync('unzip', ['-Z1', zipPath], { encoding: 'utf8' })
  .split('\n').filter(Boolean);
if (!listing.includes('index.html')) {
  problems.push('index.html is not at the root of the archive');
}
if (!listing.some((e) => e.startsWith('assets/') && !e.endsWith('/'))) {
  problems.push('the archive has no assets/ directory beside index.html');
}

// ---------------------------------------------------------------- 5. report
const zipSize = fs.statSync(zipPath).size;
console.log('');
console.log('  index.html   ' + human(fs.statSync(path.join(DIST, 'index.html')).size));
console.log('  files        ' + files.length + ' / ' + LIMITS.files);
console.log('  unpacked     ' + human(total) + ' / ' + human(LIMITS.total));
console.log('  zip          ' + human(zipSize));
console.log('  → ' + path.relative(ROOT, zipPath));

if (notes.filter((n) => !n.startsWith('pruned')).length) {
  console.log('\nNotes:');
  notes.filter((n) => !n.startsWith('pruned')).forEach((n) => console.log('  • ' + n));
}

if (problems.length) {
  console.log('\n✗ Not ready to upload:');
  problems.forEach((p) => console.log('  • ' + p));
  process.exit(1);
}
console.log('\n✓ Ready to upload.');
