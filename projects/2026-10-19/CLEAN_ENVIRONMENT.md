# Clean dependency environment verification

On October 19, 2026, a fresh Python 3.12 virtual environment was created without system-site packages. Only the declared requirements and their dependencies were installed. The complete three-stage verifier passed for both projects in that environment. The resolved environment is now pinned in `requirements.txt` and recorded in `ENVIRONMENT.txt`.

Reproduction verifies official-data fingerprints, then uses cached sources, fresh Python subprocesses and two isolated output directories, with no network during the analytical verification. All numerical/text results match the published outputs. Every generated artifact, including images, is byte-identical across two builds within the verified environment. Cross-platform figure bytes can vary; their numerical inputs and rendered structure are checked independently.

This does not claim independent human review. Browser execution is recorded separately by GitHub CI. The methods have separate hand-worked and analytical-oracle checks; figure inspection and the browser limitation are recorded in each project's `VISUAL_REVIEW.md`.
