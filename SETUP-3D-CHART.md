# 3D GitHub Contribution Chart — Setup

This repository now includes a README-compatible isometric SVG contribution chart for `deveshmitra`.

## Files and locations

Keep this exact structure in the `deveshmitra/deveshmitra` profile repository:

```text
deveshmitra/
├── README.md
├── 3d-contributions.svg              # created by the workflow
├── scripts/
│   └── generate_3d_contributions.py
└── .github/
    └── workflows/
        ├── update-3d-contributions.yml
        ├── metrics.yml               # existing workflow
        └── snake.yml                 # existing workflow
```

## Setup

1. Upload/commit the `README.md`, `scripts/` folder, and `.github/workflows/update-3d-contributions.yml`.
2. In GitHub, open **Settings → Actions → General → Workflow permissions**.
3. Select **Read and write permissions** if the repository is configured to restrict the default token to read-only, then save.
4. Open **Actions → Update 3D GitHub Contributions → Run workflow**.
5. After it succeeds, confirm `3d-contributions.svg` appears in the repository root. The README references it using `./3d-contributions.svg`.
6. The workflow also runs daily at 02:17 UTC (07:47 India Standard Time).

## Authentication

The workflow uses the automatically provided `GITHUB_TOKEN`; no personal access token or additional secret is required for the chart workflow.

The existing `metrics.yml` workflow separately references `secrets.METRICS_TOKEN`. That is unrelated to the 3D chart and must be configured separately if you want to keep using GitHub Metrics.

## Notes

- The SVG is static and compatible with GitHub README rendering. GitHub does not execute Three.js/WebGL inside README images.
- The existing `snake.yml` workflow is retained and will continue publishing its snake images to the `output` branch, but the README no longer embeds the snake.
- The contribution graph is generated from GitHub's contribution calendar. Private contribution details depend on what GitHub makes available to the token.
