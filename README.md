# GitHub Contribution Dashboard

A personal GitHub contribution analytics dashboard inspired by the GitHub activity dashboard aesthetic. Built with Next.js, TypeScript, and Tailwind CSS. Fetches **live data** from the GitHub GraphQL API — no hardcoded values, no databases, no paid services.

## Features

- **Contribution Graph** — custom grid with intensity coloring, hover tooltips, and "today" marker
- **Current-month statistics** — commits, best day, daily average, active days, current streak
- **Contribution Activity timeline** — last 4 months grouped with per-repository commit breakdown
- **Repository commit bars** — dynamic-width bars scaled to the largest repo each month
- **Summary statistics** — total commits, active repos, repos created, pull requests
- **Live/fresh data** — server-side fetch on every page load + manual refresh button
- **Loading & error states** — skeleton screens and retry UI
- **Responsive** — desktop, tablet, and mobile layouts
- **Secure** — GitHub token never leaves the server

## Tech Stack

- Next.js (App Router)
- TypeScript
- Tailwind CSS
- GitHub GraphQL API
- lucide-react (icons)

## Local Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/gitbio.git
cd gitbio
```

2. Install dependencies:

```bash
npm install
```

3. Create `.env.local` and add your GitHub token:

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```env
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=navinskyy
```

> **Token security:** Your `GITHUB_TOKEN` is read **only on the server** (in the API route). It is never prefixed with `NEXT_PUBLIC_`, never sent to the browser, and never committed to the repository. `.env.local` is listed in `.gitignore`.

4. Start the dev server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment Variables

| Variable          | Required | Description                                              |
| ----------------- | -------- | ------------------------------------------------------- |
| `GITHUB_TOKEN`    | Yes      | GitHub personal access token (server-side only)         |
| `GITHUB_USERNAME` | Yes      | GitHub username to display on the dashboard             |

### Creating a GitHub Token

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Give it a name (e.g., `gitbio-dashboard`)
4. Select the **repo** scope (read access to public repositories is sufficient for the data we fetch)
5. Copy the token and paste it into `GITHUB_TOKEN` in `.env.local`

> The token only needs `repo` scope. It is never exposed to the browser.

## How the GitHub API Works

The dashboard uses the GitHub GraphQL API (`https://api.github.com/graphql`) server-side. On each page load, the API route (`/api/github`) makes authenticated requests with the `Authorization: Bearer <token>` header and queries:

- `contributionsCollection` — contribution calendar, commit/PR/issue totals, repository breakdowns, repository creation dates
- The route fetches the current month plus the previous 3 months individually, then aggregates them into a single dashboard payload

The token is read from `process.env.GITHUB_TOKEN` inside the route handler and is never included in any client-side code.

## How the Dashboard Stays Updated

- **Fresh server fetch on every page load** — no static caching, so the dashboard reflects the latest GitHub activity
- **Manual refresh button** in the header re-fetches data on demand
- No automatic polling is configured by default to avoid hammering the GitHub API. If you want periodic refresh, add a `setInterval` in the client wrapper with a 5-minute interval.

## Deploy to Vercel

1. Push your code to GitHub:

```bash
git add -A
git commit -m "Add GitHub contribution dashboard"
git push origin main
```

2. Import the repository into [Vercel](https://vercel.com):

3. In the Vercel project settings, add the following **Environment Variables**:

   - `GITHUB_TOKEN` = your GitHub personal access token
   - `GITHUB_USERNAME` = `navinskyy`

4. Deploy. Vercel's free tier handles Next.js builds and deployments with no configuration needed.

> The project runs entirely on Vercel's free tier. No database, no paid APIs, no external services.

## 🕷️ GitHub Activity

<p align="center">
  <img
    src="https://gitbio-ruby.vercel.app/api/github-card"
    alt="Navinskyy's GitHub Contribution Activity"
    width="100%"
  />
</p>

<p align="center">
  <a href="https://gitbio-ruby.vercel.app">
    <strong>🚀 Open Interactive Dashboard</strong>
  </a>
</p>

The card is generated server-side from the same GitHub token and username configuration as the dashboard. Its statistics and heatmap are never hardcoded.

## Limitations & GitHub API Considerations

- **Rate limits:** GitHub GraphQL API allows 5,000 points per hour for authenticated requests. The dashboard makes ~5 requests per page load, so this is unlikely to be an issue for a personal dashboard.
- **Contribution calendar:** The `contributionCalendar` counts total contributions (commits, PRs, issues), not just commits. Monthly commit counts use `totalCommitContributions` from each monthly query for accuracy.
- **Private contributions:** If your contributions include private repositories, the token must have `repo` scope and the private contributions must be enabled in your GitHub settings.
- **New repositories:** Repository creation dates come from `createdAt` in `commitContributionsByRepository`. Repositories with no commit contributions in the queried period are not counted.

## License

MIT
