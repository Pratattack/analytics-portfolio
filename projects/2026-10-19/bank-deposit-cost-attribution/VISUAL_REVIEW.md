# Visual and browser verification scope

The expense-bridge PNG was visually inspected: signed driver direction, units, categories and title are legible. The static report checks local links/images, SVG XML and PNG decoding. The application separates observed research from a hypothetical repricing calculator and clearly identifies its 20-bank review-queue filter.

Actual desktop and mobile Chromium application screenshots were downloaded from CI and visually inspected. The scenario fields, calculated cards and review queue were legible; mobile tables used contained horizontal scrolling. That run subsequently failed a Firefox memo-encoding check and was not counted as a passing full browser run. The server now declares UTF-8, and selector names are explicit; consult the latest CI execution for acceptance.

The local runtime has no browser binary. Cloud-browser policy blocks local-file URLs; that action was not retried through another cloud-browser route. Actual browser acceptance runs in isolated GitHub Actions over its own localhost HTTP server.

The `october19-browser-acceptance` job checks Chromium, Firefox and WebKit at desktop 1440×1000 and mobile 390×844. Both projects' reports/applications make 24 combinations. Bank flows include reconciliation to the Python calculator, an invalid cut above the current rate, recovery, an adverse attrition case, filtering and reset; shared checks include images/links, overflow, accessible headings/names, keyboard memo navigation and browser errors.

Screenshots and `results.json` are attached as `october19-browser-evidence`. Use the actual job result at the verified commit as evidence; writing tests is not equivalent to executing them. This does not claim production, accessibility or economic-effectiveness certification, or public live hosting.
