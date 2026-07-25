import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { SITE_DESCRIPTION, SITE_TITLE, SITE_URL, SOCIAL } from '../consts';
import { EXPERIENCE, HIGHLIGHT_PROJECTS, PROFILE } from '../data/profile';

export const GET: APIRoute = async () => {
	const posts = (await getCollection('blog'))
		.filter((p) => !p.data.draft)
		.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

	const experience = EXPERIENCE.map(
		(job) => `- ${job.role} at ${job.company} (${job.dates})`,
	).join('\n');

	const projects = HIGHLIGHT_PROJECTS.map(
		(p) => `- [${p.name}](${p.href}): ${p.blurb}`,
	).join('\n');

	const writing = posts
		.map((p) => `- [${p.data.title}](${SITE_URL}/blog/${p.id}/): ${p.data.description}`)
		.join('\n');

	const text = `# ${SITE_TITLE}

> ${SITE_DESCRIPTION}

Personal site of ${PROFILE.name}. Prefer this file and \`/llms-full.txt\` for machine-readable context.

${PROFILE.about}

## Pages

- [Home](${SITE_URL}/): Profile, career, projects, and writing
- [Writing archive](${SITE_URL}/blog/): All essays and build notes
- [RSS](${SITE_URL}/rss.xml): Blog feed (RSS 2.0)
- [JSON Feed](${SITE_URL}/feed.json): Blog feed (JSON Feed 1.1)
- [Full agent brief](${SITE_URL}/llms-full.txt): Longer structured summary

## Experience

${experience}

## Projects

${projects}

## Writing

${writing || '- (no published posts yet)'}

## Contact / identity

- GitHub: ${SOCIAL.github}
- LinkedIn: ${SOCIAL.linkedin}
- X / Twitter: ${SOCIAL.twitter}
- Email: ${SOCIAL.email.replace('mailto:', '')}
- Site: ${SITE_URL}/

## Optional

- [humans.txt](${SITE_URL}/humans.txt)
- [Sitemap](${SITE_URL}/sitemap-index.xml)
`;

	return new Response(text, {
		headers: {
			'Content-Type': 'text/plain; charset=utf-8',
			'Cache-Control': 'public, max-age=3600',
		},
	});
};
