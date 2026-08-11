/**
 * Copy Glider's docs site into public/Glider/, so it publishes at
 * https://utsv.work/Glider/.
 *
 * The Glider repo stays the source of truth: glider.exe serves docs/site at
 * 127.0.0.1:8081/docs/, and the pages are edited there. This script only takes
 * a snapshot of them for the website build, because the website's Pages build
 * has no Glider checkout of its own.
 *
 *   node scripts/sync-glider-docs.mjs [path-to-glider-repo]
 *   GLIDER_REPO=D:/repos/Glider node scripts/sync-glider-docs.mjs
 *
 * Default source is ../Glider, a sibling of this repo.
 *
 * Glider's own paths are already rooted at /Glider/ (that was its GitHub Pages
 * base), so nothing needs rewriting — every link in the tree is relative.
 */

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const websiteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const gliderRepo = path.resolve(
	process.argv[2] ?? process.env.GLIDER_REPO ?? path.join(websiteRoot, '..', 'Glider'),
);
const dest = path.join(websiteRoot, 'public', 'Glider');

// What the old Glider Pages workflow assembled: the landing page plus docs/.
// The Go source, configs and planning notes deliberately stay unpublished.
const SOURCES = [
	{ from: 'index.html', to: 'index.html' },
	{ from: 'docs', to: 'docs' },
];

function fail(message) {
	console.error(`sync-glider-docs: ${message}`);
	process.exit(1);
}

if (!fs.existsSync(path.join(gliderRepo, 'index.html'))) {
	fail(
		`no Glider checkout at ${gliderRepo}\n` +
			'  pass the path as an argument or set GLIDER_REPO',
	);
}

for (const { from } of SOURCES) {
	if (!fs.existsSync(path.join(gliderRepo, from))) {
		fail(`${gliderRepo} has no ${from}`);
	}
}

// Replace the tree rather than merge into it, so a page deleted upstream also
// disappears here.
fs.rmSync(dest, { recursive: true, force: true });
fs.mkdirSync(dest, { recursive: true });

for (const { from, to } of SOURCES) {
	const source = path.join(gliderRepo, from);
	const target = path.join(dest, to);
	if (fs.statSync(source).isDirectory()) {
		fs.cpSync(source, target, { recursive: true });
	} else {
		fs.copyFileSync(source, target);
	}
}

/** Every .html file under dest, as absolute paths. */
function htmlFiles(dir) {
	const out = [];
	for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
		const full = path.join(dir, entry.name);
		if (entry.isDirectory()) out.push(...htmlFiles(full));
		else if (entry.name.endsWith('.html')) out.push(full);
	}
	return out;
}

const idsOf = (file) =>
	new Set([...fs.readFileSync(file, 'utf8').matchAll(/id="([^"]+)"/g)].map((m) => m[1]));

/**
 * Check the copy is whole: every relative link and asset reference resolves,
 * and every anchor exists in the page it points at. This catches a partial or
 * stale copy, which is the failure this script can actually cause.
 */
const broken = [];
const pages = htmlFiles(dest);

for (const page of pages) {
	const html = fs.readFileSync(page, 'utf8');
	const here = path.dirname(page);
	const ids = idsOf(page);
	const rel = path.relative(dest, page).replaceAll('\\', '/');

	const refs = [
		...[...html.matchAll(/href="([^"]+)"/g)].map((m) => m[1]),
		...[...html.matchAll(/src="([^"]+)"/g)].map((m) => m[1]),
	];

	for (const ref of refs) {
		if (/^(https?:|mailto:|data:|\/\/)/.test(ref)) continue;
		const [target, anchor] = [ref.split('#')[0], ref.split('#')[1]];

		if (!target) {
			if (anchor && !ids.has(anchor)) broken.push(`${rel}: no anchor #${anchor}`);
			continue;
		}

		const resolved = path.resolve(here, target);
		if (!fs.existsSync(resolved)) {
			broken.push(`${rel}: missing ${target}`);
			continue;
		}
		if (anchor && resolved.endsWith('.html') && !idsOf(resolved).has(anchor)) {
			broken.push(`${rel}: ${target} has no #${anchor}`);
		}
	}
}

if (broken.length) {
	fail(`the copied site has broken references:\n  ${broken.join('\n  ')}`);
}

// Record which Glider commit is live, so the published pages can be traced
// back to a revision without guessing.
let revision = 'unknown';
try {
	revision = execFileSync('git', ['-C', gliderRepo, 'rev-parse', 'HEAD'], {
		encoding: 'utf8',
	}).trim();
} catch {
	// A source tree without git history still copies fine.
}

fs.writeFileSync(
	path.join(dest, '.glider-source'),
	`source: ${gliderRepo.replaceAll('\\', '/')}\n` +
		`commit: ${revision}\n` +
		`synced: ${new Date().toISOString()}\n`,
	'utf8',
);

console.log(
	`sync-glider-docs: copied ${pages.length} pages from ${gliderRepo} → public/Glider/ ` +
		`(glider ${revision.slice(0, 7)}); all references resolve`,
);
