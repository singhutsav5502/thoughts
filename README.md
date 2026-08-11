# Utsav Singh — personal site

Blog-first static site built with [Astro](https://astro.build).

## Commands

| Command           | Action                          |
| ----------------- | ------------------------------- |
| `npm install`     | Install dependencies            |
| `npm run dev`     | Local dev server at `localhost:4321` |
| `npm run build`   | Production build to `./dist/`   |
| `npm run preview` | Preview the production build    |
| `npm run sync:glider` | Refresh `public/Glider/` from the Glider repo |

## Content

- Posts live in `src/content/blog/` (Markdown frontmatter + body)
- Projects link out to GitHub (`https://github.com/singhutsav5502`)

### `public/Glider/` is generated — do not hand-edit

The Glider product docs publish at `https://utsv.work/Glider/`, but they are
written and owned in the [Glider repo](https://github.com/singhutsav5502/Glider)
(`index.html` + `docs/`), where `glider.exe` itself serves them at
`127.0.0.1:8081/docs/`. `public/Glider/` is a committed snapshot of that tree.

`utsv.work` is the apex custom domain on this repo, and GitHub Pages allows one
repo per domain — so the Glider repo cannot serve the subpath itself. Publishing
through this build is what puts it at `/Glider/`.

To pick up Glider doc changes, from a checkout that sits beside `Glider/`:

```powershell
npm run sync:glider          # or: npm run sync:glider -- D:/path/to/Glider
git add public/Glider && git commit
```

The script replaces the tree (so upstream deletions propagate), verifies every
relative link, anchor and asset still resolves, and stamps the source commit
into `public/Glider/.glider-source`. Editing Glider's docs does **not** update
`utsv.work` until this is re-run and pushed.

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
