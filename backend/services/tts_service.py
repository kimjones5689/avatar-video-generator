"""
Talking Photo AI
Text-to-Speech Service

This module provides a provider-independent interface for
generating speech audio.

Concrete providers (local or cloud) should subclass
BaseTTSProvider.

The rest of the application should depend only on
TTSService, not on any specific speech engine.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import uuid

# ────────────────────────────────────────────────────────
# Models
# ────────────────────────────────────────────────────────

@dataclass
class SpeechRequest:
    text: str
    language: str = "en"
    voice: str = "default"
    speaking_rate: float = 1.0


@dataclass
class SpeechResult:
    success: bool
    audio_path: Optional[Path] = None
    duration_seconds: float = 0.0
    message: str = ""


# ────────────────────────────────────────────────────────
# Provider Interface
# ────────────────────────────────────────────────────────

class BaseTTSProvider(ABC):
    """
    Abstract interface implemented by all
    text-to-speech providers.
    """

    @abstractmethod
    def synthesize(
        self,
        request: SpeechRequest,
        output_path: Path,
    ) -> SpeechResult:
        pass


# ────────────────────────────────────────────────────────
# Placeholder Provider
# ────────────────────────────────────────────────────────

class PlaceholderTTSProvider(BaseTTSProvider):
    """
    Development placeholder.
    Produces no audio but allows the
    application architecture to be exercised.
    """

    def synthesize(
        self,
        request: SpeechRequest,
        output_path: Path,
    ) -> SpeechResult:
        return SpeechResult(
            success=False,
            audio_path=output_path,
            duration_seconds=0.0,
            message=(
                "No TTS provider configured. "
                "Register a supported implementation."
            ),
        )


# ────────────────────────────────────────────────────────
# Service
# ────────────────────────────────────────────────────────

class TTSService:
    def __init__(
        self,
        provider: BaseTTSProvider,
        output_directory: Path,
    ):
        self.provider = provider
        self.output_directory = output_directory
        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def generate(
        self,
        request: SpeechRequest,
    ) -> SpeechResult:
        output_file = (
            self.output_directory /
            f"{uuid.uuid4()}.wav"
        )
        return self.provider.synthesize(
            request=request,
            output_path=output_file,
        )
