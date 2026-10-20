# Visual and browser verification scope

The rendered policy-capture PNG was visually inspected: title, categories, units and axes are legible, with no observed overlap or clipping. The static report checks local image/link targets, SVG XML and PNG decoding. The application adds policy/cap controls, carrier/airport search, hypothetical pilot economics, validation and reset.

The local runtime has no browser binary. Cloud-browser policy blocks local-file URLs, and that action was not retried through another cloud-browser route. Actual browser acceptance runs in an isolated GitHub Actions environment over its own localhost HTTP server.

The `october19-browser-acceptance` job tests Chromium, Firefox and WebKit at desktop 1440×1000 and mobile 390×844, both reports and applications: 24 combinations across the two projects. It checks image/output loading, page overflow, horizontal table containers, semantic headings/link names, keyboard memo navigation, calculator reconciliation, invalid-input recovery, empty states, policy switching and reset. Screenshots and `results.json` are uploaded as the `october19-browser-evidence` artifact.

Read the actual job result at the verified commit in GitHub Actions. Test code or a static data check does not itself mean that browser execution passed. These are application-acceptance checks, not exhaustive production certification, load tests, assistive-technology certification or proof of operational effectiveness. Applications run locally; no hosted public service is claimed.
