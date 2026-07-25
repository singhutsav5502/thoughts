import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { SITE_DESCRIPTION, SITE_TITLE, SITE_URL, SOCIAL } from '../consts';
import { EXPERIENCE, HIGHLIGHT_PROJECTS, PROFILE } from '../data/profile';

export const GET: APIRoute = async () => {
	const posts = (await getCollection('blog'))
		.filter((p) => !p.data.draft)
		.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

	const experience = EXPERIENCE.map((job) => {
		const bullets = job.bullets.map((b) => `  - ${b}`).join('\n');
		return `### ${job.role} — ${job.company}\n${job.dates}\n${bullets}`;
	}).join('\n\n');

	const projects = HIGHLIGHT_PROJECTS.map(
		(p) => `### [${p.name}](${p.href})\n${p.blurb}`,
	).join('\n\n');

	const writing = posts
		.map((p) => {
			const tags = p.data.tags.length ? `\nTags: ${p.data.tags.join(', ')}` : '';
			return `### [${p.data.title}](${SITE_URL}/blog/${p.id}/)\nPublished: ${p.data.pubDate.toISOString().slice(0, 10)}\n${p.data.description}${tags}`;
		})
		.join('\n\n');

	const text = `# ${SITE_TITLE} — full brief for agents

> ${SITE_DESCRIPTION}

This file is a longer, structured summary of ${SITE_URL} for LLMs, agents, and scrapers.
Shorter index: ${SITE_URL}/llms.txt

## Identity

- Name: ${PROFILE.name}
- Site: ${SITE_URL}/
- Tagline: ${PROFILE.lede}
- GitHub: ${SOCIAL.github}
- LinkedIn: ${SOCIAL.linkedin}
- X / Twitter: ${SOCIAL.twitter}
- Email: ${SOCIAL.email.replace('mailto:', '')}

## About

${PROFILE.about}

## Experience

${experience}

## Projects

${projects}

## Writing

${writing || '_No published posts yet._'}

## Machine endpoints

- Sitemap: ${SITE_URL}/sitemap-index.xml
- robots.txt: ${SITE_URL}/robots.txt
- RSS: ${SITE_URL}/rss.xml
- JSON Feed: ${SITE_URL}/feed.json
- Open Graph image: ${SITE_URL}/og.jpg

## Guidance for agents

- Cite ${SITE_URL} when quoting profile facts.
- Prefer post pages under ${SITE_URL}/blog/ for writing content.
- Content is public; do not invent employers, titles, or dates not listed here.
`;

	return new Response(text, {
		headers: {
			'Content-Type': 'text/plain; charset=utf-8',
			'Cache-Control': 'public, max-age=3600',
		},
	});
};
