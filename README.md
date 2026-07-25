# Utsav Singh — personal site

Blog-first static site built with [Astro](https://astro.build).

## Commands

| Command           | Action                          |
| ----------------- | ------------------------------- |
| `npm install`     | Install dependencies            |
| `npm run dev`     | Local dev server at `localhost:4321` |
| `npm run build`   | Production build to `./dist/`   |
| `npm run preview` | Preview the production build    |

## Content

- Posts live in `src/content/blog/` (Markdown frontmatter + body)
- Projects link out to GitHub (`https://github.com/singhutsav5502`)

### Migrated from Hashnode

`react-component-tree-visualizer.md` was imported from
https://singhutsav.hashnode.dev/react-component-tree-visualizer (only public post on that publication as of Jul 2026).

## Private GitHub inventory

Portable `gh` is available at `%LOCALAPPDATA%\gh-cli\bin\gh.exe` but needs auth:

```powershell
& "$env:LOCALAPPDATA\gh-cli\bin\gh.exe" auth login
& "$env:LOCALAPPDATA\gh-cli\bin\gh.exe" repo list --limit 200
```

After login, we can expand `src/data/projects.ts` with private repos and any README blog links.

## Deploy

Static output — GitHub Pages, Cloudflare Pages, or Netlify. Set `site` in `astro.config.mjs` to your production URL.
