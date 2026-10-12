# app-distribution

This repository is a combined distribution source for personal CLI applications across:

- Homebrew tap manifests in `Formula/`
- Scoop bucket manifests in `bucket/`

It is designed to scale by treating `apps/*.json` as the single source of truth, then generating package-manager-specific files from GitHub Releases.

## Why this layout works

- A Homebrew tap repository only needs a `Formula/` directory with Ruby formula files.
- A Scoop bucket repository only needs a `bucket/` directory with JSON manifests.
- Keeping both in one repository lets a single release source drive both ecosystems.
- Adding a new CLI should only require one metadata file plus a regeneration step.

## Repository structure

```text
.
|-- .github/
|   `-- workflows/
|       `-- validate-generated.yml
|-- Formula/
|-- apps/
|   `-- wewa.json
|-- bucket/
|-- scripts/
|   `-- generate_manifests.py
`-- README.md
```

## Metadata model

Each app is declared in `apps/<name>.json`.

Current example: `apps/wewa.json`

- General metadata: name, description, homepage, license
- Source repository: GitHub owner/name
- Homebrew target: formula name, binary name, macOS asset mapping
- Scoop target: manifest name, executable name, Windows asset mapping

The generator reads the latest GitHub release, matches the configured asset names, and fills in version numbers, URLs, and SHA-256 values automatically.

## Packaged app

`wewa` is distributed from `https://github.com/ownself/wewa`.

Currently packaged release:

- Tag: `v0.4.1`
- Homebrew assets:
  - `wewa-macos-arm64.tar.gz`
  - `wewa-macos-x64.tar.gz`
- Scoop asset:
  - `wewa-windows-x64.zip`

## Generate manifests

Regenerate everything:

```powershell
python scripts\generate_manifests.py
```

Regenerate one app only:

```powershell
python scripts\generate_manifests.py --app wewa
```

Validate that committed files are up to date:

```powershell
python scripts\generate_manifests.py --check
```

## Homebrew usage

After publishing this repository to GitHub, use it as a tap:

```powershell
brew tap ownself/app-distribution https://github.com/ownself/app-distribution
brew install ownself/app-distribution/wewa
```

Update an existing installation:

```powershell
brew update
brew upgrade ownself/app-distribution/wewa
```

If you rename the repository, replace `ownself/app-distribution` accordingly.

## Scoop usage

After publishing this repository to GitHub, use it as a bucket:

```powershell
scoop bucket add ownself-app-distribution https://github.com/ownself/app-distribution
scoop install ownself-app-distribution/wewa
```

Update an existing installation:

```powershell
scoop update
scoop update wewa
```

If you rename the repository, replace the bucket URL and bucket name accordingly.

## Adding another CLI app

1. Create `apps/<name>.json`.
2. Point it to the source GitHub repository and expected release asset names.
3. Run `python scripts\generate_manifests.py`.
4. Commit the updated files in `Formula/` and `bucket/`.

## Notes

- The generator currently reads `releases/latest`, which is a good default for release-driven CLI distribution.
- GitHub's release API currently exposes asset digests, so SHA-256 values can be reused directly without downloading assets.
- The validation workflow ensures generated files stay in sync with app metadata and release output.
