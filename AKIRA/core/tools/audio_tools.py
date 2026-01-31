"""Audio processing tools - Speech recognition and synthesis."""

from __future__ import annotations

import os
import tempfile
from typing import Any, Dict, Optional
from pathlib import Path

from .schema import Tool, ToolResult


class AudioTranscribeTool(Tool):
    """
    Tool for transcribing audio to text using OpenAI Whisper.

    Supports multiple languages and audio formats.
    """

    def __init__(self):
        super().__init__(
            name="audio_transcribe",
            description="Transcribe audio/voice to text",
            parameters={
                "file_path": {
                    "type": "string",
                    "description": "Path to audio file"
                },
                "language": {
                    "type": "string",
                    "description": "Language code (e.g., 'ru', 'en')",
                    "required": False
                }
            }
        )

    async def execute(self, args: Dict[str, Any], context: Any) -> ToolResult:
        """Transcribe audio file to text."""
        file_path = args.get("file_path")
        language = args.get("language", "ru")

        if not file_path or not os.path.exists(file_path):
            return ToolResult(
                success=False,
                output="",
                error="Audio file not found"
            )

        try:
            # Use OpenAI Whisper API for transcription
            from openai import AsyncOpenAI

            client = AsyncOpenAI()

            with open(file_path, "rb") as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )

            return ToolResult(
                success=True,
                output=transcript.text,
                metadata={
                    "file_path": file_path,
                    "language": language,
                    "duration": transcript.duration if hasattr(transcript, 'duration') else None
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Transcription failed: {str(e)}"
            )


class AudioSynthesizeTool(Tool):
    """
    Tool for synthesizing speech from text using OpenAI TTS.

    Generates natural-sounding voice.
    """

    def __init__(self):
        super().__init__(
            name="audio_synthesize",
            description="Convert text to speech",
            parameters={
                "text": {
                    "type": "string",
                    "description": "Text to convert to speech"
                },
                "voice": {
                    "type": "string",
                    "enum": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                    "description": "Voice to use",
                    "default": "nova"
                },
                "output_path": {
                    "type": "string",
                    "description": "Path to save audio file",
                    "required": False
                }
            }
        )

    async def execute(self, args: Dict[str, Any], context: Any) -> ToolResult:
        """Synthesize speech from text."""
        text = args.get("text")
        voice = args.get("voice", "nova")
        output_path = args.get("output_path")

        if not text:
            return ToolResult(
                success=False,
                output="",
                error="Text is required"
            )

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI()

            # Generate speech
            response = await client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )

            # Save to file
            if not output_path:
                output_path = os.path.join(
                    tempfile.gettempdir(),
                    f"speech_{os.urandom(8).hex()}.mp3"
                )

            response.stream_to_file(output_path)

            return ToolResult(
                success=True,
                output=output_path,
                metadata={
                    "text": text,
                    "voice": voice,
                    "file_path": output_path
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Synthesis failed: {str(e)}"
            )


class AudioDownloadTool(Tool):
    """
    Tool for downloading audio from Telegram.

    Handles voice messages and audio files.
    """

    def __init__(self):
        super().__init__(
            name="audio_download",
            description="Download audio from Telegram",
            parameters={
                "file_id": {
                    "type": "string",
                    "description": "Telegram file ID"
                },
                "output_path": {
                    "type": "string",
                    "description": "Path to save file",
                    "required": False
                }
            }
        )

    async def execute(self, args: Dict[str, Any], context: Any) -> ToolResult:
        """Download audio file from Telegram."""
        file_id = args.get("file_id")
        output_path = args.get("output_path")

        if not file_id:
            return ToolResult(
                success=False,
                output="",
                error="file_id is required"
            )

        try:
            # This will be implemented with Telegram bot integration
            # For now, return placeholder

            if not output_path:
                output_path = os.path.join(
                    tempfile.gettempdir(),
                    f"telegram_audio_{file_id[:8]}.ogg"
                )

            # TODO: Implement actual download using aiogram
            # bot = context.get_bot()
            # file = await bot.get_file(file_id)
            # await bot.download_file(file.file_path, output_path)

            return ToolResult(
                success=True,
                output=output_path,
                metadata={
                    "file_id": file_id,
                    "file_path": output_path
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Download failed: {str(e)}"
            )
