"""Curriculum & Sampling Scheduler
Created: August 22, 2025
Author: GitHub Copilot

Category 4 (Curriculum / Sampling Strategy).
Provides progressive phase schedule and sampling weights adjustments.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CurriculumPhase:
    name: str
    start_step: int
    end_step: int
    image_prob: float
    audio_prob: float
    max_seq_len: int

class CurriculumScheduler:
    def __init__(self, phases: list[CurriculumPhase]):
        self.phases = phases

    def current(self, step: int) -> CurriculumPhase:
        for ph in self.phases:
            if ph.start_step <= step < ph.end_step:
                return ph
        return self.phases[-1]

DEFAULT_CURRICULUM = CurriculumScheduler([
    CurriculumPhase("bootstrap", 0, 1000, image_prob=0.3, audio_prob=0.3, max_seq_len=256),
    CurriculumPhase("expand", 1000, 4000, image_prob=0.5, audio_prob=0.5, max_seq_len=384),
    CurriculumPhase("full", 4000, 1000000, image_prob=0.7, audio_prob=0.7, max_seq_len=512),
])
