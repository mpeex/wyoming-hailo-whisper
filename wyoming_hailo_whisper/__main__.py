#!/usr/bin/env python3
import argparse
import asyncio
import logging
import platform
import re
from functools import partial
import os
from wyoming_hailo_whisper.app.hailo_whisper_pipeline import HailoWhisperPipeline
from wyoming.info import AsrModel, AsrProgram, Attribution, Info
from wyoming.server import AsyncServer

from . import __version__
from .handler import HailoWhisperEventHandler

_LOGGER = logging.getLogger(__name__)


def get_encoder_hef_path(hw_arch):
    """
    Get the HEF path for the encoder based on the Hailo hardware architecture.

    Args:
        hw_arch (str): Hardware architecture ("hailo8" or "hailo8l").

    Returns:
        str: Path to the encoder HEF file.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    if hw_arch == "hailo8l":
        hef_path = os.path.join(base_path, 'app', 'hefs', 'h8l', 'tiny', 'tiny-whisper-encoder-10s_15dB_h8l.hef')
    else:
        hef_path = os.path.join(base_path, 'app', 'hefs', 'h8', 'tiny', 'tiny-whisper-encoder-10s_15dB.hef')
    if not os.path.exists(hef_path):
        raise FileNotFoundError(f"Encoder HEF file not found: {hef_path}. Please check the path.")
    return hef_path


def get_decoder_hef_path(hw_arch):
    """
    Get the HEF path for the decoder based on the Hailo hardware architecture and host type.

    Args:
        hw_arch (str): Hardware architecture ("hailo8" or "hailo8l").
        host (str): Host type ("x86" or "arm64").

    Returns:
        str: Path to the decoder HEF file.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    if hw_arch == "hailo8l":
        hef_path = os.path.join(base_path, 'app', "hefs", "h8l", "tiny", "tiny-whisper-decoder-fixed-sequence-matmul-split_h8l.hef")
    else:
        hef_path = os.path.join(base_path, 'app', "hefs", "h8", "tiny", "tiny-whisper-decoder-fixed-sequence-matmul-split.hef")
    if not os.path.exists(hef_path):
        raise FileNotFoundError(f"Decoder HEF file not found: {hef_path}. Please check the path.")
    return hef_path

async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", required=True, help="unix:// or tcp://")
    parser.add_argument(
        "--device",
        default="hailo8l",
        help="Device to use for inference (default: hailo8l)",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Default language to set for transcription",
    )
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    parser.add_argument(
        "--log-format", default=logging.BASIC_FORMAT, help="Format for log messages"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print version and exit",
    )
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO, format=args.log_format
    )
    _LOGGER.debug(args)

    args.language = "en"
    model_name = "whisper hailo model"

    wyoming_info = Info(
        asr=[
            AsrProgram(
                name="hailo-whisper",
                description="Hailo accelerated Whisper",
                attribution=Attribution(
                    name="mpeex",
                    url="",
                ),
                installed=True,
                version=__version__,
                models=[
                    AsrModel(
                        name=model_name,
                        description=model_name,
                        attribution=Attribution(
                            name="Systran",
                            url="https://huggingface.co/Systran",
                        ),
                        installed=True,
                        languages=["en"],
                        version=__version__,
                    )
                ],
            )
        ],
    )

    # Load model
    _LOGGER.debug("Loading %s", model_name)
    encoder_path = get_encoder_hef_path(args.device)
    decoder_path = get_decoder_hef_path(args.device)
    whisper_model = HailoWhisperPipeline(encoder_path, decoder_path, "tiny", True)

    server = AsyncServer.from_uri(args.uri)
    _LOGGER.info("Ready")
    model_lock = asyncio.Lock()
    await server.run(
        partial(
            HailoWhisperEventHandler,
            wyoming_info,
            args,
            whisper_model,
            model_lock,
        )
    )


# -----------------------------------------------------------------------------


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
