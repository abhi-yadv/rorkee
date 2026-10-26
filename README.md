# Campus Carbon Footprint Mapper

A React and TypeScript portfolio prototype for exploring building-level emissions, department comparisons and a simple daily emissions simulation.

**Status: learning prototype.** The dashboard uses sample data from `src/lib/mockData.ts`; chat responses are scripted. This repository does not establish an official affiliation with IIT Roorkee, live sensor integration, verified emission reductions or green certifications. Institutional names and locations in the original demo are illustrative.

## What works today

- Dashboard summaries, building filters and department comparisons over sample data.
- Time-of-day simulation and a map analytics interface.
- Scripted chat and sample recommendation history.
- Responsive layouts and nested routes with React Router.

The Supabase client and domain interfaces are scaffolding. The current dashboard does not load records from a database. The original team profiles, contact form and project milestones are demo content, not verified people or outcomes.

## Run locally

Use Node.js 22 LTS and npm.

```sh
git clone https://github.com/abhi-yadv/rorkee.git
cd rorkee
npm ci
npm run dev
```

The sample dashboard runs without Supabase. If you extend `src/lib/supabase.ts`, copy `.env.example` to `.env.local` and configure your own development project. Browser-prefixed variables are public; never put a service-role key in them.

The map expects a separately configured Mappls SDK. Without it, use the sample data views; the map is not a live geographic visualization.

## Checks

```sh
npm run typecheck
npm run lint
npm run build
npm run preview
```

Output is written to `dist/`. Static hosting must serve `index.html` for application routes such as `/dashboard/overview`.

## Structure

```text
src/components/       Navigation and layouts
src/lib/mockData.ts    Sample buildings, routes and locations
src/lib/types.ts       Domain interfaces
src/pages/Dashboard/   Overview, simulation and map views
src/pages/Chat/        Scripted chat and sample history
src/pages/About/       Project information
```

## Development priorities

1. Document emission factors, units, assumptions and provenance before importing measured data.
2. Add tests for totals, filters and simulation boundaries, followed by CI.
3. Replace sample team/contact content with verified maintainer information.
4. Add accessible chart descriptions and export the filtered dataset.
5. Introduce authentication and a validated backend when persistence is needed.
6. Add screenshots and a short walkthrough that labels sample data.

## Ownership and licensing

Maintained by [Abhishek Yadav](https://github.com/abhi-yadv). No open-source license has been added. Confirm ownership and third-party asset rights before choosing one.
