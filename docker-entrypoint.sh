#!/usr/bin/env bash
#source /home/wyoming_hailo_whisper/.venv/bin/activate
python3 -m wyoming_hailo_whisper \
    --uri 'tcp://0.0.0.0:10600' \
    --device 'hailo8l' \
    --variant 'tiny'