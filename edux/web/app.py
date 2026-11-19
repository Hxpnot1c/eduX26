"""The web layer: static pages and a small JSON API, served by the same process as the MCP endpoint.

Routing (see `WebLayer`): /mcp goes to the MCP app behind the student key check, exactly as before. The pages and
/static carry no data, so they are public. Everything with data is under /api and needs a key sent as a bearer header,
never in the URL (a URL ends up in logs, history and screenshots). A student key opens the student API; a teacher key
opens the teacher API; neither opens the other, and a teacher key never opens /mcp. A map link from get_my_progress is
swapped once at POST /api/link for a short session that opens the student API like a key (see `links`, decision 0026).

Every response from this layer carries a strict content security policy: pages load nothing from another origin, so a
pupil's address is never sent to a font or script host."""

from __future__ import annotations

import json
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import BaseRoute, Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from edux import learner, teachers
from edux.web import actions, links, views

STATIC = Path(__file__).resolve().parent / "static"

PAGES = {"/": "index.html", "/map": "map.html", "/me": "me.html", "/teacher": "teacher.html"}

SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; manifest-src 'self'; "
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
    """Who the bearer key belongs to: ("student", student) or ("teacher", teacher), or None. A session from a map link
    counts as its student (the student API is read-only). A key in the URL is never accepted (the caller refuses the
    request first, see `refuse_url_key`)."""
    key = _bearer(request)
    if not key:
        return None
    student = learner.student_by_key(key) or links.student_by_session(key)
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


async def api_map(request: Request) -> Response:
    """The course map (structure only) for any signed-in student or teacher. A student gets their own course; a teacher
    names one with ?course= when more than one is loaded."""
    refused = refuse_url_key(request)
    if refused:
        return refused
    found = principal(request)
    if found is None:
        return unauthorised()
    role, who = found
    wanted = who.get("course_id") if role == "student" else request.query_params.get("course")
    data = views.course_map(wanted)
    if data is None:
        return JSONResponse({"error": "no such course; name one with ?course="}, status_code=404)
    return JSONResponse(data)


async def api_me(request: Request) -> Response:
    """The signed-in student's own page data. A teacher key is refused: a teacher never reads one student's record."""
    refused = refuse_url_key(request)
    if refused:
        return refused
    found = principal(request)
    if found is None:
        return unauthorised()
    role, who = found
    if role != "student":
        return JSONResponse({"error": "this page is for students; teachers see classes, not one student's record"}, status_code=403)
    return JSONResponse(views.student_page(who))


async def api_teacher_class(request: Request) -> Response:
    """One class, at class level only. A student key is refused; a teacher sees only classes assigned to them, and a class
    that is not theirs is a 404, so its existence is not revealed."""
    refused = refuse_url_key(request)
    if refused:
        return refused
    found = principal(request)
    if found is None:
        return unauthorised()
    role, who = found
    if role != "teacher":
        return JSONResponse({"error": "this page is for teachers"}, status_code=403)
    class_id = request.path_params["class_id"]
    if not teachers.may_see(who["id"], class_id):
        return JSONResponse({"error": "no such class"}, status_code=404)
    return JSONResponse(views.class_summary(class_id))


MAX_BODY = 16_000


async def _teacher_class(request: Request) -> tuple[dict, str] | Response:
    """The signed-in teacher and the class from the path, or the response to send instead (401, 400, 403 or 404)."""
    refused = refuse_url_key(request)
    if refused:
        return refused
    found = principal(request)
    if found is None:
        return unauthorised()
    role, who = found
    if role != "teacher":
        return JSONResponse({"error": "this page is for teachers"}, status_code=403)
    class_id = request.path_params["class_id"]
    if not teachers.may_see(who["id"], class_id):
        return JSONResponse({"error": "no such class"}, status_code=404)
    return who, class_id


async def _json_body(request: Request) -> dict | Response:
    raw = await request.body()
    if len(raw) > MAX_BODY:
        return JSONResponse({"error": "that request is too large"}, status_code=413)
    try:
        body = json.loads(raw or b"{}")
    except ValueError:
        return JSONResponse({"error": "the request body must be JSON"}, status_code=400)
    return body if isinstance(body, dict) else JSONResponse({"error": "the request body must be a JSON object"}, status_code=400)


def _acted(class_id: str, ok: bool, error: str | None) -> Response:
    if not ok:
        return JSONResponse({"error": error}, status_code=400)
    return JSONResponse(views.class_summary(class_id))


async def api_teacher_assessment(request: Request) -> Response:
    """Set a test or assignment for the whole class."""
    got = await _teacher_class(request)
    if isinstance(got, Response):
        return got
    teacher, class_id = got
    body = await _json_body(request)
    if isinstance(body, Response):
        return body
    return _acted(class_id, *actions.set_assessment(teacher["id"], class_id, body))


async def api_teacher_assessment_remove(request: Request) -> Response:
    got = await _teacher_class(request)
    if isinstance(got, Response):
        return got
    teacher, class_id = got
    body = await _json_body(request)
    if isinstance(body, Response):
        return body
    return _acted(class_id, *actions.remove_assessment(teacher["id"], class_id, body.get("id")))


async def api_teacher_coverage(request: Request) -> Response:
    """Mark sections as taught to the class."""
    got = await _teacher_class(request)
    if isinstance(got, Response):
        return got
    teacher, class_id = got
    body = await _json_body(request)
    if isinstance(body, Response):
        return body
    return _acted(class_id, *actions.set_coverage(teacher["id"], class_id, body))


async def api_link(request: Request) -> Response:
    """Swap a map link token, once, for a session token: {"session", "expires_in"}. A used, expired or unknown token gets
    401 and the page tells the student to ask for a new link."""
    refused = refuse_url_key(request)
    if refused:
        return refused
    body = await _json_body(request)
    if isinstance(body, Response):
        return body
    token = body.get("token")
    swapped = links.exchange(token) if isinstance(token, str) else None
    if swapped is None:
        return JSONResponse({"error": "this link has already been used or has expired"}, status_code=401)
    return JSONResponse(swapped)


async def api_public_map(request: Request) -> Response:
    """The map of the synthetic example pack, with no key, if web.public_example_map is on. Any other pack: 404."""
    if not learner._settings().web.public_example_map:
        return JSONResponse({"error": "not available"}, status_code=404)
    data = views.course_map(views.EXAMPLE_COURSE_ID)
    if data is None:
        return JSONResponse({"error": "not available"}, status_code=404)
    return JSONResponse(data)


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


async def favicon(request: Request) -> Response:
    """/favicon.ico, for browsers and tools that ask for it at the root rather than reading the page's icon links."""
    return FileResponse(STATIC / "brand" / "favicon.ico", media_type="image/vnd.microsoft.icon")


def build_web_app() -> ASGIApp:
    routes: list[BaseRoute] = [Route(path, _page(name), methods=["GET"]) for path, name in PAGES.items()]
    routes.append(Route("/favicon.ico", favicon, methods=["GET"]))
    routes.append(Route("/api/whoami", whoami, methods=["GET"]))
    routes.append(Route("/api/map", api_map, methods=["GET"]))
    routes.append(Route("/api/public/map", api_public_map, methods=["GET"]))
    routes.append(Route("/api/me", api_me, methods=["GET"]))
    routes.append(Route("/api/link", api_link, methods=["POST"]))
    routes.append(Route("/api/teacher/class/{class_id}", api_teacher_class, methods=["GET"]))
    routes.append(Route("/api/teacher/class/{class_id}/assessments", api_teacher_assessment, methods=["POST"]))
    routes.append(Route("/api/teacher/class/{class_id}/assessments/remove", api_teacher_assessment_remove, methods=["POST"]))
    routes.append(Route("/api/teacher/class/{class_id}/coverage", api_teacher_coverage, methods=["POST"]))
    routes.append(Mount("/static", StaticFiles(directory=STATIC), name="static"))
    return _Headers(Starlette(routes=routes))


def is_web_path(path: str) -> bool:
    return path in PAGES or path == "/favicon.ico" or path.startswith(("/static/", "/api/"))


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
