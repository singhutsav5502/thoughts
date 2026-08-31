// @ts-check

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import { defineConfig, fontProviders } from 'astro/config';

const SITE = 'https://utsv.work';

const GLIDER_DIR = fileURLToPath(new URL('./public/Glider', import.meta.url));

/**
 * Every `.html` page under `public/Glider/`, as absolute URLs.
 *
 * `@astrojs/sitemap` only enumerates Astro routes, and the Glider docs are a
 * committed snapshot in `public/` (see README) — so without this the sitemap
 * ships three URLs and none of the 13 Glider pages.
 *
 * Walked from disk rather than hand-listed so `npm run sync:glider` can add or
 * remove pages upstream without the sitemap silently drifting out of step —
 * same reasoning as the case-repair map in `src/pages/404.astro`.
 *
 * URLs are emitted in the form the site actually links to: `/Glider/` for the
 * landing page (how `HIGHLIGHT_PROJECTS` links it), and the explicit
 * `index.html` for nested hubs (how the landing page links them). Nothing in
 * the tree sets `rel=canonical`, so declaring a different spelling here would
 * invent a second URL for the same content.
 */
function gliderPages() {
	/** @type {string[]} */
	const urls = [];

	/** @param {string} dir */
	const walk = (dir) => {
		for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
			const full = path.join(dir, entry.name);
			if (entry.isDirectory()) {
				walk(full);
				continue;
			}
			if (!entry.name.endsWith('.html')) continue;

			const rel = path.relative(GLIDER_DIR, full).split(path.sep).join('/');
			urls.push(rel === 'index.html' ? `${SITE}/Glider/` : `${SITE}/Glider/${rel}`);
		}
	};

	walk(GLIDER_DIR);
	return urls.sort();
}

const gliderUrls = gliderPages();

// The one way this breaks invisibly: an empty snapshot yields an empty list and
// the Glider docs quietly leave the sitemap again.
if (gliderUrls.length === 0) {
	throw new Error(
		`No .html pages found under ${GLIDER_DIR} — the Glider snapshot is missing or empty, so the sitemap would omit /Glider/ entirely. Run \`npm run sync:glider\`.`,
	);
}

// https://astro.build/config
export default defineConfig({
	site: SITE,
	integrations: [
		mdx(),
		sitemap({
			filter: (page) => !page.includes('/about'),
			customPages: gliderUrls,
			changefreq: 'weekly',
			priority: 0.7,
			lastmod: new Date(),
		}),
	],
	fonts: [
		{
			provider: fontProviders.fontsource(),
			name: 'Fraunces',
			cssVariable: '--font-display',
			weights: [600],
			styles: ['normal'],
			subsets: ['latin'],
			fallbacks: ['Georgia', 'serif'],
		},
		{
			provider: fontProviders.fontsource(),
			name: 'IBM Plex Sans',
			cssVariable: '--font-body',
			weights: [400, 600],
			styles: ['normal'],
			subsets: ['latin'],
			fallbacks: ['system-ui', 'sans-serif'],
		},
		{
			provider: fontProviders.fontsource(),
			name: 'IBM Plex Mono',
			cssVariable: '--font-mono',
			weights: [400],
			styles: ['normal'],
			subsets: ['latin'],
			fallbacks: ['ui-monospace', 'monospace'],
		},
	],
});
