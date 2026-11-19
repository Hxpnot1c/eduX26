"""The web layer: static pages and a small JSON API, served by the same process as the MCP endpoint.

Routing (see `WebLayer`): /mcp goes to the MCP app behind the student key check, exactly as before. The pages and
/static carry no data, so they are public. Everything with data is under /api and needs a key sent as a bearer header,
never in the URL (a URL ends up in logs, history and screenshots). A student key opens the student API; a teacher key
opens the teacher API; neither opens the other, and a teacher key never opens /mcp.

Every response from this layer carries a strict content security policy: pages load nothing from another origin, so a
pupil's address is never sent to a font or script host."""

from __future__ import annotations

from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import BaseRoute, Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from edux import learner, teachers

STATIC = Path(__file__).resolve().parent / "static"

PAGES = {"/": "index.html", "/map": "map.html", "/me": "me.html", "/teacher": "teacher.html"}

SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; "
        "base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
    ),
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), interest-cohort=()",
}


def _bearer(request: Request) -> str | None:
    header = request.headers.get("authorization", "")
    scheme, _, value = header.partition(" ")
    return value.strip() if scheme.lower() == "bearer" and value.strip() else None


def principal(request: Request) -> tuple[str, dict] | None:
    """Who the bearer key belongs to: ("student", student) or ("teacher", teacher), or None. A key in the URL is never
    accepted (the caller refuses the request first, see `refuse_url_key`)."""
    key = _bearer(request)
    if not key:
        return None
    student = learner.student_by_key(key)
    if student:
        return "student", student
    teacher = teachers.teacher_by_key(key)
    return ("teacher", teacher) if teacher else None


def refuse_url_key(request: Request) -> Response | None:
    """A 400 if the request carries a key in its query string: it would be logged and kept in history."""
    if "key" in request.query_params:
        return JSONResponse({"error": "send the key in the Authorization header (Bearer), not in the URL"}, status_code=400)
    return None


def unauthorised() -> Response:
    return JSONResponse({"error": "unknown or missing key; open the link you were given"}, status_code=401)


async def whoami(request: Request) -> Response:
    """Who the key belongs to, and for a teacher which classes they may see. Never returns the key or a name for a student."""
    refused = refuse_url_key(request)
    if refused:
        return refused
    found = principal(request)
    if found is None:
        return unauthorised()
    role, who = found
    if role == "teacher":
        return JSONResponse({"role": "teacher", "name": who["name"], "classes": teachers.classes_of(who["id"])})
    return JSONResponse({"role": "student"})


def _page(name: str):
    async def handler(request: Request) -> Response:
        return FileResponse(STATIC / name, media_type="text/html; charset=utf-8", headers={"Cache-Control": "no-cache"})

    return handler


class _Headers:
    """ASGI middleware: add the security headers to every response, and no-store to the API."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        api = scope["path"].startswith("/api/")

        async def wrapped(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                present = {k.lower() for k, _ in headers}
                for name, value in SECURITY_HEADERS.items():
                    if name.lower().encode() not in present:
                        headers.append((name.lower().encode(), value.encode()))
                if api and b"cache-control" not in present:
                    headers.append((b"cache-control", b"no-store"))
            await send(message)

        await self.app(scope, receive, wrapped)


def build_web_app() -> ASGIApp:
    routes: list[BaseRoute] = [Route(path, _page(name), methods=["GET"]) for path, name in PAGES.items()]
    routes.append(Route("/api/whoami", whoami, methods=["GET"]))
    routes.append(Mount("/static", StaticFiles(directory=STATIC), name="static"))
    return _Headers(Starlette(routes=routes))


def is_web_path(path: str) -> bool:
    return path in PAGES or path.startswith(("/static/", "/api/"))


class WebLayer:
    """Send the pages, /static and /api to the web app and everything else (the MCP endpoint, the lifespan) to `inner`."""

    def __init__(self, inner: ASGIApp) -> None:
        self.inner = inner
        self.web = build_web_app()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and is_web_path(scope["path"]):
            await self.web(scope, receive, send)
        else:
            await self.inner(scope, receive, send)
