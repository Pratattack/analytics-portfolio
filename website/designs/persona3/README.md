# Persona 3 inspired portfolio preview

This design lives at `/design-preview/persona3/`. The production homepage and all 26 existing project routes are unchanged. The preview includes selected work, the complete searchable library, all case-study copy, About, resume and contact. Analytical tools and downloads link to the preserved existing URLs.

## Rebuild

Run `python designs/persona3/build.py` from the website checkout. It reads `content/published-projects.json`, writes only the preview folder, and copies its original SVG, licensed fonts, CSS and JS. The preview does not use reference-repository source or media.

## Restore

`restore-point.json` pins production version 7 and the matching pushed source commit. To restore the complete pre-preview deployment, deploy that exact saved version with Sites. To remove the separate preview while retaining the current site, remove `dist/design-preview/persona3/` and publish a new version. The GitHub backup branch pins the original source and all analytical projects. Neither DNS nor HTTPS configuration changes.

## Promote after approval

The main site has not been switched. Before promotion, adapt the existing build script to emit the new shell for each real project URL, keep all original slugs, preserve downloads and tools, and remove preview labels/noindex from production pages only. Re-run navigation, filter, copy and preservation checks. Preview hash routes are for review and do not replace canonical project paths.

## Verification limit

No browser was operated, in accordance with the owner’s instruction. Static references, source preservation, JS syntax, route parsing, filters and generated case content are checked. Mobile rendering, focus traversal, PDF embedding and audio playback need browser verification before claiming those pass.
