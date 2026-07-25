export const PROFILE = {
	name: 'Utsav Singh',
	avatar: 'https://github.com/singhutsav5502.png?size=240',
	quirk: '⛰️ ☕ 💻',
	lede: 'Fullstack engineer interested in financial systems, building agentic systems and AI/ML.',
	about: `I'm currently a Spring Analyst Intern at Morgan Stanley, working on financial data dashboards and microservice integrations. Before that I was a Frontend Engineer Intern at Zamp, where I shipped marketing surfaces and an internal agentic chatbot.`,
} as const;

export type Experience = {
	company: string;
	role: string;
	dates: string;
	bullets: string[];
};

export const EXPERIENCE: Experience[] = [
	{
		company: 'Morgan Stanley',
		role: 'Spring Analyst Intern',
		dates: 'Jan 2026 – Present',
		bullets: [
			'Built financial data dashboards processing up to 500K rows of daily data',
			'Designed modular microservice architecture integrating with multiple existing codebases',
		],
	},
	{
		company: 'Zamp',
		role: 'Frontend Engineer Intern',
		dates: 'May 2025 – Aug 2025',
		bullets: [
			'Led brand remarketing POC and built the company site with Next.js, Framer Motion, and Tailwind',
			'Built an internal agentic chatbot integrating N8N, Supabase, Notion, and Slack',
		],
	},
];

export type HighlightProject = {
	name: string;
	blurb: string;
	href: string;
};

export const HIGHLIGHT_PROJECTS: HighlightProject[] = [
	{
		name: 'Glider',
		blurb:
			'Local AI harness above Cursor — gateway/MITM routing, Loop Engineering hoops, swarms, and per-run workspaces.',
		href: '/blog/glider-orchestration/',
	},
	{
		name: 'Graphite Editor',
		blurb:
			'Open-source contributions (Rust / Wasm / TypeScript) — measurement overlays, node catalog filtering, transform cage work; 6+ merged PRs.',
		href: 'https://graphite.rs',
	},
	{
		name: 'React Tree Visualiser',
		blurb:
			'Parse React JS/JSX into an AST and render the component tree with React Flow.',
		href: 'https://react-tree-visualiser-frontend.vercel.app/',
	},
	{
		name: 'Admin Dashboard',
		blurb: 'MERN admin dashboard with Redux Toolkit, Material UI, and server-side pagination.',
		href: 'https://github.com/singhutsav5502/adminDashboardMERN',
	},
];
