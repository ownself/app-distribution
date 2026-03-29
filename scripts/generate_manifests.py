#!/usr/bin/env python3
"""Generate Homebrew and Scoop manifests from app metadata and GitHub releases."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
APPS_DIR = REPO_ROOT / "apps"
FORMULA_DIR = REPO_ROOT / "Formula"
BUCKET_DIR = REPO_ROOT / "bucket"
USER_AGENT = "ownself-app-distribution-manifest-generator/1.0"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Homebrew Formula and Scoop bucket manifests from apps/*.json.",
    )
    parser.add_argument(
        "--app",
        action="append",
        dest="apps",
        help="Only generate specific app(s) by metadata file stem. Repeatable.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify generated files are up to date without writing them.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app_files = discover_app_files(args.apps)
    stale_files: list[Path] = []

    for app_file in app_files:
        app = load_json(app_file)
        release = fetch_latest_release(app["repository"]["owner"], app["repository"]["name"])
        targets = app.get("targets", {})

        if "homebrew" in targets:
            formula_path = FORMULA_DIR / f'{targets["homebrew"]["formula_name"]}.rb'
            formula_content = render_formula(app, targets["homebrew"], release)
            write_or_check(formula_path, formula_content, args.check, stale_files)

        if "scoop" in targets:
            manifest_path = BUCKET_DIR / f'{targets["scoop"]["manifest_name"]}.json'
            manifest_content = render_scoop_manifest(app, targets["scoop"], release)
            write_or_check(manifest_path, manifest_content, args.check, stale_files)

    if args.check and stale_files:
        print("Generated files are out of date:", file=sys.stderr)
        for path in stale_files:
            print(f"  - {path.relative_to(REPO_ROOT)}", file=sys.stderr)
        return 1

    return 0


def discover_app_files(selected_apps: list[str] | None) -> list[Path]:
    app_files = sorted(APPS_DIR.glob("*.json"))
    if not selected_apps:
        return app_files

    selected = set(selected_apps)
    filtered = [path for path in app_files if path.stem in selected]
    missing = selected.difference({path.stem for path in filtered})
    if missing:
        raise SystemExit(f"Unknown app metadata file(s): {', '.join(sorted(missing))}")
    return filtered


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_latest_release(owner: str, repo: str) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
        },
    )

    try:
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"Failed to fetch latest release for {owner}/{repo}: {exc}") from exc


def render_formula(app: dict[str, Any], target: dict[str, Any], release: dict[str, Any]) -> str:
    version = normalize_version(release["tag_name"])
    class_name = ruby_class_name(target["formula_name"])

    arm_asset = release_asset(release, target["macos"]["arm64"])
    x64_asset = release_asset(release, target["macos"]["x64"])

    docs = target.get("docs", [])
    doc_lines = "\n".join(
        f'    doc.install "{doc}" if File.exist?("{doc}")' for doc in docs
    )
    if doc_lines:
        doc_lines = f"\n{doc_lines}"

    return (
        f"class {class_name} < Formula\n"
        f'  desc "{ruby_string(app["description"])}"\n'
        f'  homepage "{app["homepage"]}"\n'
        f'  version "{version}"\n'
        f'  license "{app["license"]}"\n'
        f"\n"
        f"  on_macos do\n"
        f"    if Hardware::CPU.arm?\n"
        f'      url "{arm_asset["browser_download_url"]}"\n'
        f'      sha256 "{asset_sha256(arm_asset)}"\n'
        f"    else\n"
        f'      url "{x64_asset["browser_download_url"]}"\n'
        f'      sha256 "{asset_sha256(x64_asset)}"\n'
        f"    end\n"
        f"  end\n"
        f"\n"
        f"  def install\n"
        f'    bin.install "{target["binary"]}"'
        f"{doc_lines}\n"
        f"  end\n"
        f"\n"
        f"  test do\n"
        f'    system "#{{bin}}/{target["binary"]}", "--help"\n'
        f"  end\n"
        f"end\n"
    )


def render_scoop_manifest(app: dict[str, Any], target: dict[str, Any], release: dict[str, Any]) -> str:
    version = normalize_version(release["tag_name"])
    windows_target = target["windows"]
    architecture: dict[str, Any] = {}
    autoupdate_architecture: dict[str, Any] = {}

    for arch, asset_name in windows_target.items():
        asset = release_asset(release, asset_name)
        architecture[arch] = {
            "url": asset["browser_download_url"],
            "hash": asset_sha256(asset),
        }
        autoupdate_architecture[arch] = {
            "url": github_release_url_template(app, asset_name),
        }

    manifest = {
        "version": version,
        "description": app["description"],
        "homepage": app["homepage"],
        "license": app["license"],
        "architecture": architecture,
        "bin": target["binary"],
        "checkver": "github",
        "autoupdate": {
            "architecture": autoupdate_architecture,
        },
    }
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def write_or_check(path: Path, content: str, check: bool, stale_files: list[Path]) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return

    if check:
        stale_files.append(path)
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def normalize_version(tag_name: str) -> str:
    return tag_name[1:] if tag_name.startswith("v") else tag_name


def ruby_class_name(name: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", name)
    return "".join(part[:1].upper() + part[1:] for part in parts if part)


def ruby_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def github_release_url_template(app: dict[str, Any], asset_name: str) -> str:
    owner = app["repository"]["owner"]
    repo = app["repository"]["name"]
    return f"https://github.com/{owner}/{repo}/releases/download/v$version/{asset_name}"


def release_asset(release: dict[str, Any], asset_name: str) -> dict[str, Any]:
    for asset in release.get("assets", []):
        if asset["name"] == asset_name:
            return asset
    raise SystemExit(f"Missing release asset: {asset_name}")


def asset_sha256(asset: dict[str, Any]) -> str:
    digest = asset.get("digest")
    if not digest or not digest.startswith("sha256:"):
        raise SystemExit(f'Missing sha256 digest for asset: {asset["name"]}')
    return digest.split(":", 1)[1]


if __name__ == "__main__":
    raise SystemExit(main())
