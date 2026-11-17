"""Load settings.toml and context.toml into typed dataclasses and compute settings_hash.

Every teaching or scoring number lives in settings.toml; what the chatbot is given
lives in context.toml and text/. Missing, unknown or mistyped keys fail loudly at startup.
"""

from __future__ import annotations

import dataclasses
import hashlib
import tomllib
import typing
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = ROOT / "settings.toml"
CONTEXT_PATH = ROOT / "context.toml"
TEXT_DIR = ROOT / "text"


class SettingsError(ValueError):
    """A settings or context file is missing a key, has an unknown key or a wrong type."""


@dataclass(frozen=True)
class Levels:
    new: float
    secure: float


@dataclass(frozen=True)
class SlipGuess:
    slip: float
    guess: float


@dataclass(frozen=True)
class Bkt:
    prior: float
    learn_rate: float
    correct_share: float
    evidence: dict[str, SlipGuess]


@dataclass(frozen=True)
class Nudges:
    depth: dict[str, float]
    engagement: dict[str, float]
    concept_tag_strength: float


@dataclass(frozen=True)
class Evidence:
    immediate_window_minutes: float


@dataclass(frozen=True)
class Offloading:
    guess_after: float
    checks_discounted: int


@dataclass(frozen=True)
class Decay:
    base_half_life_days: float
    on_success: float
    on_failure: float
    min_half_life_days: float
    seen_refresh: float


@dataclass(frozen=True)
class Propagation:
    prereq_boost: float
    queue_band: tuple[float, float]


@dataclass(frozen=True)
class Importance:
    w_exam: float
    w_dependents: float


@dataclass(frozen=True)
class Scheduling:
    share_far: float
    share_mid: float
    share_near: float
    min_gap_days: float
    just_show_me_gap_days: float
    max_reviews_per_reply: int
    untested_after: int
    untested_below: float


@dataclass(frozen=True)
class Support:
    worked_example_below: float
    hint_below: float
    extend_from: float
    procedural_types: list[str]


@dataclass(frozen=True)
class TeachingNote:
    max_words: int
    exam_close_days: int
    approach_min_records: int


@dataclass(frozen=True)
class Prequestion:
    enabled: bool
    max_options: int
    min_distractors: int
    exchange_weight: float
    full_weight_at: float


@dataclass(frozen=True)
class Session:
    gap_minutes: float
    fatigue_min_minutes: float
    fatigue_window: int
    fatigue_threshold: float
    fatigue_min_parts: int
    fatigue_slip_add: float
    slip_cap: float
    signal_window: int
    stuck_attempts: int
    stuck_below: float
    quick_parts: int
    pattern_min_sessions: int


@dataclass(frozen=True)
class Difficulty:
    default: float
    prior_shift: float
    half_life_shift: float
    w_cross: float


@dataclass(frozen=True)
class LinkWeight:
    base: float
    w_exam: float
    w_material: float
    w_misconception: float
    material_source_types: list[str]
    suggest_min_questions: int


@dataclass(frozen=True)
class Resolve:
    name_boost: float
    candidate_ratio: float


@dataclass(frozen=True)
class Progress:
    levers: int
    weak_links: int
    trend_days: int
    trend_min_change: float


@dataclass(frozen=True)
class Blocks:
    review_link_boost: float
    review_importance_floor: float
    confusable_mixup: float
    confusable_mention: float
    causal_mention: float
    causal_cues: list[str]
    exam_w_marks: float
    exam_w_closeness: float
    exam_w_command: float
    exam_horizon_days: float


@dataclass(frozen=True)
class Style:
    max_words: int


@dataclass(frozen=True)
class Settings:
    """Typed view of settings.toml."""

    protocol: str
    levels: Levels
    bkt: Bkt
    nudges: Nudges
    evidence: Evidence
    offloading: Offloading
    decay: Decay
    propagation: Propagation
    importance: Importance
    authority: dict[str, int]
    scheduling: Scheduling
    support: Support
    teaching_note: TeachingNote
    prequestion: Prequestion
    session: Session
    difficulty: Difficulty
    link_weight: LinkWeight
    resolve: Resolve
    progress: Progress
    blocks: Blocks
    style: Style


@dataclass(frozen=True)
class Profile:
    blocks: list[str]
    plan: bool                 # false: tutor_turn returns no plan (a comparison profile)


@dataclass(frozen=True)
class ContextConfig:
    """Typed view of context.toml: default profile, profiles and their blocks, limits."""

    default_profile: str
    profiles: dict[str, Profile]
    limits: dict[str, int]


def _convert(value: object, tp: object, where: str) -> object:
    """Check value against the type hint tp and build dataclasses; raise SettingsError on mismatch."""
    origin = typing.get_origin(tp)
    if dataclasses.is_dataclass(tp):
        if not isinstance(value, dict):
            raise SettingsError(f"{where}: expected a table")
        return _build(tp, value, where)
    if origin is dict:
        _, value_tp = typing.get_args(tp)
        if not isinstance(value, dict):
            raise SettingsError(f"{where}: expected a table")
        return {k: _convert(v, value_tp, f"{where}.{k}") for k, v in value.items()}
    if origin in (list, tuple):
        args = typing.get_args(tp)
        if not isinstance(value, list):
            raise SettingsError(f"{where}: expected an array")
        if origin is tuple:
            if len(value) != len(args):
                raise SettingsError(f"{where}: expected {len(args)} items, got {len(value)}")
            return tuple(_convert(v, a, f"{where}[{i}]") for i, (v, a) in enumerate(zip(value, args)))
        return [_convert(v, args[0], f"{where}[{i}]") for i, v in enumerate(value)]
    if tp is float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SettingsError(f"{where}: expected a number, got {value!r}")
        return float(value)
    if tp is int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise SettingsError(f"{where}: expected an integer, got {value!r}")
        return value
    if tp is str:
        if not isinstance(value, str):
            raise SettingsError(f"{where}: expected a string, got {value!r}")
        return value
    if tp is bool:
        if not isinstance(value, bool):
            raise SettingsError(f"{where}: expected true or false, got {value!r}")
        return value
    raise SettingsError(f"{where}: unsupported type {tp}")


def _build(cls: type, data: dict, where: str) -> object:
    hints = typing.get_type_hints(cls)
    names = [f.name for f in dataclasses.fields(cls)]
    missing = [n for n in names if n not in data]
    unknown = [k for k in data if k not in names]
    if missing:
        raise SettingsError(f"{where}: missing {', '.join(missing)}")
    if unknown:
        raise SettingsError(f"{where}: unknown {', '.join(unknown)}")
    prefix = f"{where}." if where else ""
    return cls(**{n: _convert(data[n], hints[n], f"{prefix}{n}") for n in names})


def _read_toml(path: Path) -> dict:
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except FileNotFoundError as e:
        raise SettingsError(f"{path} not found") from e
    except tomllib.TOMLDecodeError as e:
        raise SettingsError(f"{path}: {e}") from e


def load_settings(path: Path = SETTINGS_PATH) -> Settings:
    """Parse settings.toml, raising on a missing, unknown or mistyped key."""
    settings = _build(Settings, _read_toml(path), "")
    if not 0 < settings.levels.new < settings.levels.secure < 1:
        raise SettingsError("levels: expected 0 < new < secure < 1")
    return settings


def load_context(path: Path = CONTEXT_PATH) -> ContextConfig:
    """Parse context.toml, raising on a missing, unknown or mistyped key."""
    context = _build(ContextConfig, _read_toml(path), "")
    if context.default_profile not in context.profiles:
        raise SettingsError(f"default_profile: no profile named {context.default_profile!r}")
    return context


def settings_hash(settings_path: Path = SETTINGS_PATH, context_path: Path = CONTEXT_PATH) -> str:
    """First 8 hex characters of the SHA-256 of settings.toml plus context.toml."""
    digest = hashlib.sha256(settings_path.read_bytes() + context_path.read_bytes())
    return digest.hexdigest()[:8]


def protocol_label(settings: Settings, profile: str) -> str:
    """Protocol recorded on events: the settings protocol plus the context profile, e.g. "v0.1/full"."""
    return f"{settings.protocol}/{profile}"


def read_text(relative_path: str) -> str:
    """Read a markdown file from text/, e.g. "tools/log_exchange.md"."""
    return (TEXT_DIR / relative_path).read_text(encoding="utf-8")
