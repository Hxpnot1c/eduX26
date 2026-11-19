"""The Synapse logo and icons: every page shows the logo and links the favicons and manifest, the files are served, the
folder stays small, and the MCP server lists its icons only when there is a public URL to give."""

import json
import re
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from edux import server
from edux.web import app as web

BRAND = Path(web.STATIC) / "brand"
FILES = [
    "synapse-logo.png",
    "synapse-icon-16.png",
    "synapse-icon-32.png",
    "synapse-icon-180.png",
    "synapse-icon-192.png",
    "synapse-icon-512.png",
    "favicon.ico",
    "site.webmanifest",
]


@pytest.fixture()
def client(course):
    return TestClient(server.http_app(), raise_server_exceptions=False)


@pytest.mark.parametrize("path", list(web.PAGES))
def test_every_page_shows_the_logo_and_links_the_icons(client, path):
    html = client.get(path).text
    assert '<link rel="icon" href="/static/brand/favicon.ico"' in html
    assert 'sizes="32x32" href="/static/brand/synapse-icon-32.png"' in html
    assert 'sizes="16x16" href="/static/brand/synapse-icon-16.png"' in html
    assert '<link rel="apple-touch-icon" sizes="180x180" href="/static/brand/synapse-icon-180.png"' in html
    assert '<link rel="manifest" href="/static/brand/site.webmanifest"' in html
    header = re.search(r'<header class="masthead">\s*<a class="wordmark" href="/">(.*?)</a>', html)
    assert header and '<img src="/static/brand/synapse-logo.png" alt="Synapse"' in header.group(1)
    assert 'href="data:,"' not in html


@pytest.mark.parametrize("name", FILES)
def test_the_brand_files_are_served(client, name):
    res = client.get(f"/static/brand/{name}")
    assert res.status_code == 200 and res.content == (BRAND / name).read_bytes()
    assert res.headers["content-security-policy"]


def test_the_favicon_is_also_at_the_root(client):
    res = client.get("/favicon.ico")
    assert res.status_code == 200 and res.content == (BRAND / "favicon.ico").read_bytes()


def test_the_policy_allows_the_manifest_and_nothing_wider(client):
    csp = client.get("/").headers["content-security-policy"]
    assert "manifest-src 'self'" in csp and "img-src 'self' data:" in csp and "default-src 'none'" in csp


def test_the_manifest_names_the_192_and_512_icons():
    manifest = json.loads((BRAND / "site.webmanifest").read_text(encoding="utf-8"))
    sizes = {icon["sizes"]: icon["src"] for icon in manifest["icons"]}
    assert sizes == {"192x192": "/static/brand/synapse-icon-192.png", "512x512": "/static/brand/synapse-icon-512.png"}
    assert manifest["name"] == "Synapse"


def test_the_brand_folder_stays_under_200_kb():
    assert sum(path.stat().st_size for path in BRAND.iterdir()) < 200_000


def test_the_mcp_server_lists_its_icons_at_the_public_url(course, monkeypatch):
    monkeypatch.setenv("EDUX_PUBLIC_BASE_URL", "https://synapse.example/")
    icons = server.build_server()._mcp_server.create_initialization_options().icons or []
    assert [(i.src, i.mimeType, i.sizes) for i in icons] == [
        ("https://synapse.example/static/brand/synapse-icon-192.png", "image/png", ["192x192"]),
        ("https://synapse.example/static/brand/synapse-icon-512.png", "image/png", ["512x512"]),
    ]


def test_the_mcp_server_sends_no_icons_without_a_public_url(course, monkeypatch):
    monkeypatch.setenv("EDUX_PUBLIC_BASE_URL", "")
    from edux.web import links

    monkeypatch.setattr(links, "public_base_url", lambda: "")
    assert server.build_server()._mcp_server.create_initialization_options().icons is None


def test_the_readme_shows_the_logo_by_a_relative_path():
    readme = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
    first = readme.splitlines()[0]
    assert first == '<img src="edux/web/static/brand/synapse-logo.png" alt="Synapse" width="96">'
