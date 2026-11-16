"""Load settings.toml and context.toml into typed dataclasses and compute settings_hash.

Every teaching or scoring number lives in settings.toml; what the chatbot is given
lives in context.toml and text/. Missing or mistyped keys fail loudly at startup.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = ROOT / "settings.toml"
CONTEXT_PATH = ROOT / "context.toml"
TEXT_DIR = ROOT / "text"


@dataclass(frozen=True)
class Settings:
    """Typed view of settings.toml (protocol, levels, bkt, nudges, decay, scheduling, ...)."""


@dataclass(frozen=True)
class ContextConfig:
    """Typed view of context.toml: default profile, profiles and their blocks, limits."""


def load_settings(path: Path = SETTINGS_PATH) -> Settings:
    """Parse settings.toml, raising on a missing or mistyped key."""
    raise NotImplementedError


def load_context(path: Path = CONTEXT_PATH) -> ContextConfig:
    """Parse context.toml, raising on a missing or mistyped key."""
    raise NotImplementedError


def settings_hash(settings_path: Path = SETTINGS_PATH, context_path: Path = CONTEXT_PATH) -> str:
    """First 8 hex characters of the SHA-256 of settings.toml plus context.toml."""
    raise NotImplementedError


def protocol_label(settings: Settings, profile: str) -> str:
    """Protocol recorded on events: the settings protocol plus the context profile, e.g. "v0.1/full"."""
    raise NotImplementedError


def read_text(relative_path: str) -> str:
    """Read a markdown file from text/, e.g. "tools/log_exchange.md"."""
    raise NotImplementedError
