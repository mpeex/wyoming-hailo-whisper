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
from wyoming_hailo_whisper.app.whisper_hef_registry import HEF_REGISTRY

from . import __version__
from .handler import HailoWhisperEventHandler

_LOGGER = logging.getLogger(__name__)

def get_hef_path(model_variant: str, hw_arch: str, component: str) -> str:
    """
    Method to retrieve HEF path.

    Args:
        model_variant (str): e.g. "tiny", "base"
        hw_arch (str): e.g. "hailo8", "hailo8l"
        component (str): "encoder" or "decoder"

    Returns:
        str: Absolute path to the requested HEF file.
    """
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        hef_registry = HEF_REGISTRY[model_variant][hw_arch][component]
        hef_path = os.path.join(base_path, hef_registry)
    except KeyError as e:
        raise FileNotFoundError(
            f"HEF not available for model '{model_variant}' on hardware '{hw_arch}'."
        ) from e

    if not os.path.exists(hef_path):
        raise FileNotFoundError(f"HEF file not found at: {hef_path}\nIf not done yet, please run ./download_resources.sh from the app/ folder to download the required HEF files.")
    return hef_path

async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", required=True, help="unix:// or tcp://")
    parser.add_argument(
        "--device",
        type=str,
        default="hailo8",
        choices=["hailo8", "hailo8l"],
        help="Hardware architecture to use (default: hailo8)"
    )
    parser.add_argument(
        "--variant",
        type=str,
        default="base",
        choices=["base", "tiny"],
        help="Whisper variant to use (default: base)"
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Default language to set for transcription",
    )
    parser.add_argument(
        "--multi-process-service", 
        action="store_true", 
        help="Enable multi-process service to run other models in addition to Whisper"
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

    #args.language = "en"
    model_name = "whisper hailo model"

    wyoming_info = Info(
        asr=[
            AsrProgram(
                name="hailo-whisper",
                description="Hailo accelerated Whisper",
                attribution=Attribution(
                    name="mpeex",
                    url="https://github.com/mpeex/wyoming-hailo-whisper",
                ),
                installed=True,
                version=__version__,
                models=[
                    AsrModel(
                        name=model_name,
                        description=model_name,
                        attribution=Attribution(
                            name="hailo.ai",
                            url="https://hailo.ai",
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
    encoder_path = get_hef_path(args.variant, args.device, "encoder")
    decoder_path = get_hef_path(args.variant, args.device, "decoder")

    whisper_model = HailoWhisperPipeline(encoder_path, decoder_path, args.variant, multi_process_service=args.multi_process_service)
    _LOGGER.info("Device %s", args.device)
    _LOGGER.info("Encoder %s", encoder_path)
    _LOGGER.info("Decoder %s", decoder_path)
    _LOGGER.info("Language %s", args.language)
    _LOGGER.info("Variant %s", args.variant)

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
