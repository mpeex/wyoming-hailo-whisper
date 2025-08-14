#!/usr/bin/with-contenv bashio
CONFIG_PATH=/data/options.json

DEVICE=$(bashio::config 'device')
VARIANT=$(bashio::config 'variant')

DEVICE="hailo8l"
VARIANT="base"

bashio::log.info "Init Wyoming Hailo device '$DEVICE' with Whisper model '$VARIANT'"
cd /home/wyoming_hailo_whisper
python3 -m wyoming_hailo_whisper \
    --uri 'tcp://0.0.0.0:10600' \
    --device "$DEVICE" \
    --variant "$VARIANT"
