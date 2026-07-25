import { getCollection } from 'astro:content';
import { SITE_DESCRIPTION, SITE_TITLE, SITE_URL, SOCIAL } from '../consts';

export async function GET() {
	const posts = (await getCollection('blog'))
		.filter((post) => !post.data.draft)
		.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

	const feed = {
		version: 'https://jsonfeed.org/version/1.1',
		title: SITE_TITLE,
		home_page_url: `${SITE_URL}/`,
		feed_url: `${SITE_URL}/feed.json`,
		description: SITE_DESCRIPTION,
		language: 'en-US',
		icon: `${SITE_URL}/apple-touch-icon.png`,
		favicon: `${SITE_URL}/favicon.ico`,
		authors: [
			{
				name: SITE_TITLE,
				url: `${SITE_URL}/`,
				avatar: 'https://github.com/singhutsav5502.png?size=240',
			},
		],
		_social: {
			github: SOCIAL.github,
			linkedin: SOCIAL.linkedin,
			twitter: SOCIAL.twitter,
		},
		items: posts.map((post) => ({
			id: `${SITE_URL}/blog/${post.id}/`,
			url: `${SITE_URL}/blog/${post.id}/`,
			title: post.data.title,
			summary: post.data.description,
			date_published: post.data.pubDate.toISOString(),
			date_modified: (post.data.updatedDate ?? post.data.pubDate).toISOString(),
			tags: post.data.tags,
			image: post.data.heroImage,
			authors: [{ name: SITE_TITLE, url: `${SITE_URL}/` }],
		})),
	};

	return new Response(JSON.stringify(feed, null, 2), {
		headers: {
			'Content-Type': 'application/feed+json; charset=utf-8',
			'Cache-Control': 'public, max-age=3600',
		},
	});
}
