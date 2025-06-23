#!/usr/bin/with-contenv bashio
python3 -m wyoming_hailo_whisper \
    --uri 'tcp://0.0.0.0:10600' \
    --device 'hailo8l'