"""Load settings.toml and context.toml into typed dataclasses and compute settings_hash.

Every teaching or scoring number lives in settings.toml; what the chatbot is given
lives in context.toml and text/. Missing, unknown or mistyped keys fail loudly at startup.
"""

from __future__ import annotations

import dataclasses
import hashlib
import math
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


MCQ_TYPES = ("mcq", "mcq_check", "prequestion", "ail_how")   # evidence types that can come from a multiple-choice question
MIN_OPTIONS = 2            # the fewest options a multiple-choice question can show, so its largest guess is 1 / 2


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
    mcq_guess_from_options: bool
    evidence: dict[str, SlipGuess]


@dataclass(frozen=True)
class Nudges:
    depth: dict[str, float]
    engagement: dict[str, float]
    ceiling: float
    concept_tag_strength: float


@dataclass(frozen=True)
class Evidence:
    immediate_window_minutes: float


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
    review_when_below: float
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
    exchange_weight: float
    full_weight_at: float


@dataclass(frozen=True)
class Points:
    max_words: int
    max_words_requested: int
    reteach_limit: int
    warn_min: int
    warn_max: int


@dataclass(frozen=True)
class Mcq:
    max_options: int
    min_distractors: int


@dataclass(frozen=True)
class Literacy:
    importance: float
    secure_every: int
    max_followups: int
    max_waits: int
    ask_min_features: int
    how_secure_every: int


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
class Engagement:
    passive_run: int
    low_share: float
    weakest_last_n: int
    coasting_min_messages: int


@dataclass(frozen=True)
class Show:
    max_per_part_session: int


@dataclass(frozen=True)
class Personalisation:
    enabled: bool
    learn_rate_k: float
    min_observations: int
    min_parts: int
    recency_half_life: float
    surprise_scale: float
    learn_rate_weight_bounds: tuple[float, float]
    max_change_per_session: float
    down_change_factor: float


@dataclass(frozen=True)
class Priorities:
    weight_homework: float
    weight_class_test: float
    weight_mock: float
    weight_final: float
    horizon_days: float
    urgency_floor: float


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
    exam_cues: list[str]
    exam_w_marks: float
    exam_w_closeness: float
    exam_w_command: float
    exam_horizon_days: float


@dataclass(frozen=True)
class Style:
    max_words: int
    length_known_share: float
    length_fatigued_share: float


@dataclass(frozen=True)
class Results:
    max_chars: int
    max_chars_full_progress: int


@dataclass(frozen=True)
class Instructions:
    max_words: int
    max_sentences: int
    cue_max_words: int


@dataclass(frozen=True)
class Settings:
    """Typed view of settings.toml."""

    protocol: str
    levels: Levels
    bkt: Bkt
    nudges: Nudges
    evidence: Evidence
    decay: Decay
    propagation: Propagation
    importance: Importance
    authority: dict[str, int]
    scheduling: Scheduling
    support: Support
    teaching_note: TeachingNote
    prequestion: Prequestion
    points: Points
    mcq: Mcq
    literacy: Literacy
    session: Session
    engagement: Engagement
    show: Show
    personalisation: Personalisation
    priorities: Priorities
    difficulty: Difficulty
    link_weight: LinkWeight
    resolve: Resolve
    progress: Progress
    blocks: Blocks
    style: Style
    results: Results
    instructions: Instructions


@dataclass(frozen=True)
class Profile:
    blocks: list[str]
    plan: bool                 # false: tutor_turn returns no plan (a comparison profile)


@dataclass(frozen=True)
class MoveReference:
    reference: list[str]       # reference blocks this move uses, in priority order (step 05c)


@dataclass(frozen=True)
class WatchFor:
    moves: list[str]           # moves that ask something also get the part's watch-for misconceptions (step 05c)


@dataclass(frozen=True)
class ContextConfig:
    """Typed view of context.toml: default profile, profiles and their blocks, limits, the reference blocks
    each move uses and the moves that get watch-for misconceptions."""

    default_profile: str
    profiles: dict[str, Profile]
    limits: dict[str, int]
    moves: dict[str, MoveReference]
    watch_for: WatchFor


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
    if not 0 < settings.nudges.ceiling < settings.levels.new:
        raise SettingsError("nudges.ceiling: expected 0 < ceiling < levels.new, so conversation alone always leaves a part at 'new'")
    low, high = settings.personalisation.learn_rate_weight_bounds
    if not 0 < low <= 1 <= high:
        raise SettingsError("personalisation.learn_rate_weight_bounds: expected 0 < low <= 1 <= high")
    if settings.points.max_words_requested < settings.points.max_words:
        raise SettingsError("points.max_words_requested: expected at least points.max_words")
    check_identifiable(settings)
    return settings


def _largest_guess(settings: Settings, evidence_type: str) -> float:
    """The largest guess an evidence type can be applied with: 1 / MIN_OPTIONS for a multiple-choice type when
    bkt.mcq_guess_from_options is on."""
    guess = settings.bkt.evidence[evidence_type].guess
    if settings.bkt.mcq_guess_from_options and evidence_type in MCQ_TYPES:
        guess = max(guess, 1 / MIN_OPTIONS)
    return guess


def personal_learn_rate(learn_rate: float, offset: float) -> float:
    """bkt.learn_rate with a student's log-odds offset applied (personal-learning-rate)."""
    odds = learn_rate / (1 - learn_rate) * math.exp(offset)
    return odds / (1 + odds)


def check_identifiable(settings: Settings) -> None:
    """Raise unless every evidence type's BKT parameters are identifiable (Baker, Corbett & Aleven, 2008), with
    slip at its largest (session.slip_cap while fatigued) and guess at its largest (immediate evidence takes the
    larger of immediate's guess and the type's own): guess + slip < 1, so a correct answer is evidence of knowing,
    and learn_rate < 1 - slip / (1 - guess), so a wrong answer still lowers the estimate. learn_rate is taken at
    the top of personalisation.learn_rate_weight_bounds, the largest a student's own rate can be."""
    bkt, cap = settings.bkt, settings.session.slip_cap
    learn_rate = personal_learn_rate(bkt.learn_rate, math.log(settings.personalisation.learn_rate_weight_bounds[1]))
    immediate = bkt.evidence.get("immediate")
    for name, sg in bkt.evidence.items():
        guesses = [_largest_guess(settings, name)]
        if immediate is not None:
            guesses.append(max(immediate.guess, guesses[0]))
        slips = [max(sg.slip, cap)] + ([max(immediate.slip, cap)] if immediate is not None else [])
        for slip, guess in zip(slips, guesses):
            if guess + slip >= 1:
                raise SettingsError(f"bkt.evidence.{name}: guess {guess:.2f} + slip {slip:.2f} (at slip_cap) must be below 1")
            if learn_rate >= 1 - slip / (1 - guess):
                raise SettingsError(f"bkt.evidence.{name}: learn_rate {learn_rate:.2f} (at the top personal bound) must be below "
                                    f"1 - slip / (1 - guess) = {1 - slip / (1 - guess):.2f} (slip at slip_cap)")


def load_context(path: Path = CONTEXT_PATH) -> ContextConfig:
    """Parse context.toml, raising on a missing, unknown or mistyped key."""
    context = _build(ContextConfig, _read_toml(path), "")
    if context.default_profile not in context.profiles:
        raise SettingsError(f"default_profile: no profile named {context.default_profile!r}")
    known = set(context.profiles[context.default_profile].blocks) | {b for p in context.profiles.values() for b in p.blocks}
    for key, move in context.moves.items():
        unknown = [b for b in move.reference if b not in known]
        if unknown:
            raise SettingsError(f"moves.{key}.reference: no profile has block(s) {', '.join(unknown)}")
    return context


def settings_hash(settings_path: Path = SETTINGS_PATH, context_path: Path = CONTEXT_PATH) -> str:
    """First 8 hex characters of the SHA-256 of settings.toml plus context.toml."""
    digest = hashlib.sha256(settings_path.read_bytes() + context_path.read_bytes())
    return digest.hexdigest()[:8]


def protocol_label(settings: Settings, profile: str) -> str:
    """Protocol recorded on events: the settings protocol plus the context profile, e.g. "v0.1/full"."""
    return f"{settings.protocol}/{profile}"


def read_text(relative_path: str) -> str:
    """Read a markdown file from text/, e.g. "tools/tutor_turn.md"."""
    return (TEXT_DIR / relative_path).read_text(encoding="utf-8")
