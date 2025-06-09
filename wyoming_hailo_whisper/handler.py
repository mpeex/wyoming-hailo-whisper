"""Event handler for clients of the server."""
import argparse
import asyncio
import io
import time
import logging
import wave

import numpy as np
from wyoming_hailo_whisper.app.hailo_whisper_pipeline import HailoWhisperPipeline
from wyoming_hailo_whisper.common.preprocessing import preprocess, improve_input_audio
from wyoming_hailo_whisper.common.postprocessing import clean_transcription

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioChunkConverter, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler

_LOGGER = logging.getLogger(__name__)


class HailoWhisperEventHandler(AsyncEventHandler):
    """Event handler for clients."""

    def __init__(
        self,
        wyoming_info: Info,
        cli_args: argparse.Namespace,
        model: HailoWhisperPipeline,
        model_lock: asyncio.Lock,
        *args,
        #initial_prompt: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
        self.model = model
        self.model_lock = model_lock
        self.audio = bytes()
        self.audio_converter = AudioChunkConverter(
            rate=16000,
            width=2,
            channels=1,
        )
        self._language = self.cli_args.language or "en"

    async def handle_event(self, event: Event) -> bool:
        if AudioChunk.is_type(event.type):
            if not self.audio:
                _LOGGER.debug("Receiving audio")

            chunk = AudioChunk.from_event(event)
            chunk = self.audio_converter.convert(chunk)
            self.audio += chunk.audio

            return True

        if AudioStop.is_type(event.type):
            _LOGGER.debug("Audio stopped")
            text = ""
            with io.BytesIO() as wav_io:
                wav_file: wave.Wave_write = wave.open(wav_io, "wb")
                with wav_file:
                    wav_file.setframerate(16000)
                    wav_file.setsampwidth(2)
                    wav_file.setnchannels(1)
                    wav_file.writeframes(self.audio)

                wav_io.seek(0)
                wav_bytes = wav_io.getvalue()

                sampled_audio = np.frombuffer(wav_bytes, dtype=np.int16).flatten().astype(np.float32) / 32768.0
                sampled_audio, start_time = improve_input_audio(sampled_audio, vad=True)

                chunk_offset = start_time - 0.2
                if chunk_offset < 0:
                    chunk_offset = 0

                chunk_length = 10

                mel_spectrograms = preprocess(
                    sampled_audio,
                    True,#self.is_nhwc,
                    chunk_length=chunk_length,
                    chunk_offset=chunk_offset
                )
                #assert self.model_proc.stdin is not None
                #assert self.model_proc.stdout is not None

                async with self.model_lock: 
                    for mel in mel_spectrograms:
                        self.model.send_data(mel)
                        time.sleep(0.2)
                        transcription = clean_transcription(self.model.get_transcription())

                text = transcription.replace("[BLANK_AUDIO]", "").strip()

            _LOGGER.info(text)

            await self.write_event(Transcript(text=text).event())
            _LOGGER.debug("Completed request")

            # Reset
            self.audio = bytes()
            self._language = self.cli_args.language

            return False

        if Transcribe.is_type(event.type):
            transcribe = Transcribe.from_event(event)
            if transcribe.language:
                self._language = transcribe.language
                _LOGGER.debug("Language set to %s", transcribe.language)
            return True

        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        return True

