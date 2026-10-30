# Persona 3 inspired portfolio preview

This design lives at `/design-preview/persona3/`. The approved design is now applied to the production homepage and all canonical project routes. The preview includes selected work, the complete searchable library, all case-study copy, About, resume and contact. Analytical tools and downloads link to the preserved existing URLs.

## Rebuild

Run `python designs/persona3/build.py` from the website checkout. It reads `content/published-projects.json`, writes only the preview folder, and copies its original SVG, licensed fonts, CSS and JS. The preview does not use reference-repository source or media.

## Restore

`restore-point.json` pins production version 7 and the matching pushed source commit. To restore the complete pre-preview deployment, deploy that exact saved version with Sites. To remove the separate preview while retaining the current site, remove `dist/design-preview/persona3/` and publish a new version. The GitHub backup branch pins the original source and all analytical projects. Neither DNS nor HTTPS configuration changes.

## Production build

Run `python scripts/build.py --projects-source /path/to/analytics-portfolio` from the website checkout. The retained charcoal builder prepares project outputs and metadata, then `build_site.py` server-renders the new theme at every canonical project URL. `site-app.js` shares its pure view functions with the static renderer, so browser navigation and direct links show the same source content. Hash routes remain available for old links and preview review. The design preview stays noindex; production pages have canonical metadata and a sitemap.

## Verification limit

No browser was operated, in accordance with the owner’s instruction. Static references, source preservation, JS syntax, route parsing, filters and generated case content are checked. Mobile rendering, focus traversal, PDF embedding and audio playback need browser verification before claiming those pass.
