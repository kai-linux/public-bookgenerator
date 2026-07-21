"""Durable manuscript continuation and bounded recovery contracts."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Mapping


@dataclass(frozen=True)
class ManuscriptState:
    job_id: str
    premise: str
    genre: str
    language: str
    quality_tier: str
    story_bible: Mapping[str, Any]
    chapters: tuple[str, ...]
    story_chapter_count: int
    continuable_prefix: bool = True


@dataclass(frozen=True)
class ContinuationPlan:
    state: ManuscriptState
    requested_total_chapters: int
    resume_chapters: tuple[str, ...]
    billable_chapters: int


def prepare_continuation(
    state: ManuscriptState, requested_total_chapters: int
) -> ContinuationPlan:
    """Resume the same artifact and bill only chapters not already present."""
    existing = len(state.chapters)
    if requested_total_chapters < existing:
        raise ValueError("continuation cannot discard existing chapters")
    if requested_total_chapters > state.story_chapter_count:
        raise ValueError("continuation exceeds the planned story length")

    updated = replace(
        state,
        continuable_prefix=requested_total_chapters < state.story_chapter_count,
    )
    return ContinuationPlan(
        state=updated,
        requested_total_chapters=requested_total_chapters,
        resume_chapters=state.chapters,
        billable_chapters=requested_total_chapters - existing,
    )


class RecoveryDecision(str, Enum):
    PRESERVE_CLEAN_OUTPUT = "preserve_clean_output"
    FAIL_HARD = "fail_hard"


def recovery_decision(
    *,
    clean_output: bool,
    small_quality_miss: bool,
    safe: bool,
    provider_completed: bool,
    artifact_usable: bool,
) -> RecoveryDecision:
    """Only a small quality-target miss may preserve otherwise clean prose."""
    if not safe or not provider_completed or not artifact_usable:
        return RecoveryDecision.FAIL_HARD
    if clean_output and small_quality_miss:
        return RecoveryDecision.PRESERVE_CLEAN_OUTPUT
    return RecoveryDecision.FAIL_HARD
