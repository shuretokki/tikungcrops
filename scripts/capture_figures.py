# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Capture the website figures for the laporan from a running site.

Every element marked with `data-figure="<name>"` on the pages below is saved as
`<out>/<name>.png`. The site is captured in light mode at twice the screen resolution,
with a small margin around each element.

Usage: start the site (`just site-dev`), then run `just figures`.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import urllib.request
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

PAGES = ["/", "/ringkasan", "/metode"]
PADDING = 24
VIEWPORT = {"width": 1280, "height": 900}
# MapLibre draws tiles after the canvas appears, so give it time to settle
MAP_SETTLE_MS = 3000


def load_everything(page: Page) -> None:
    """Scroll through the page so lazy parts render, then return to the top."""
    height = page.evaluate("document.body.scrollHeight")
    for y in range(0, height, VIEWPORT["height"] // 2):
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(150)
    page.evaluate("window.scrollTo(0, 0)")
    if page.locator(".maplibregl-canvas").count():
        page.wait_for_selector(".maplibregl-canvas")
        page.wait_for_timeout(MAP_SETTLE_MS)


def capture(page: Page, out: Path) -> list[str]:
    """Save every `data-figure` element on the current page and return the names."""
    saved = []
    width = page.evaluate("document.documentElement.scrollWidth")
    for element in page.locator("[data-figure]").all():
        name = element.get_attribute("data-figure")
        box = element.evaluate(
            "e => { const r = e.getBoundingClientRect();"
            " return {x: r.left + scrollX, y: r.top + scrollY, width: r.width, height: r.height} }"
        )
        x, y = max(box["x"] - PADDING, 0), max(box["y"] - PADDING, 0)
        clip = {
            "x": x,
            "y": y,
            "width": min(box["width"] + 2 * PADDING, width - x),
            "height": box["height"] + 2 * PADDING,
        }
        page.screenshot(path=out / f"{name}.png", clip=clip, full_page=True)
        saved.append(str(name))
    return saved


def main() -> None:
    """Capture every `data-figure` element on `PAGES` from the site at `--base-url`."""
    parser = argparse.ArgumentParser(description="Capture the website figures for the laporan.")
    parser.add_argument("--base-url", default="http://localhost:3017")
    parser.add_argument("--out", type=Path, default=Path("documents/laporan-akhir/gambar"))
    parser.add_argument("--chromium", default=shutil.which("chromium"), help="Chromium binary, default from PATH")
    args = parser.parse_args()
    try:
        urllib.request.urlopen(args.base_url, timeout=10)
    except OSError as err:
        sys.exit(f"{args.base_url} is not reachable ({err}). Start the site first: just site-dev")
    if not args.chromium:
        sys.exit("No chromium found. Pass --chromium or put chromium on PATH.")
    args.out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.chromium)
        context = browser.new_context(viewport=VIEWPORT, device_scale_factor=2)
        # the site defaults to dark mode, the laporan is printed on white
        context.add_init_script("localStorage.setItem('nuxt-color-mode', 'light')")
        page = context.new_page()
        for path in PAGES:
            page.goto(args.base_url + path, wait_until="networkidle")
            load_everything(page)
            for name in capture(page, args.out):
                print(f"{path:12} -> {args.out / name}.png")
        browser.close()


if __name__ == "__main__":
    main()
