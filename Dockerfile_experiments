
FROM ubuntu:22.04

RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone
ARG DEBIAN_FRONTEND=noninteractive

RUN mkdir /home/wyoming_hailo_whisper
WORKDIR /home/wyoming_hailo_whisper
COPY ./hailo_packages/ ./hailo_packages/
COPY ./script/ ./script/
COPY ./wyoming_hailo_whisper/ ./wyoming_hailo_whisper/
COPY ./requirements.txt ./
COPY ./docker-entrypoint.sh ./
COPY ./start-hailo-example.sh ./
COPY ./setup.* ./
COPY ./LICENSE.md ./

# Update package manager (apt-get) 
# and install (with the yes flag `-y`)
# Python and Pip
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3.10-distutils \
    python3-tk \
    python3-pip \
    python3-venv \
    ffmpeg \
    libportaudio2 \
    wget \
    pipewire \
    alsa-utils \
    pipewire-audio-client-libraries \
    libspa-0.2-bluetooth \
    vim

RUN dpkg --unpack hailo_packages/hailort_4.20.0_arm64.deb 

RUN script/setup && script/package
ENV PATH="/home/wyoming_hailo_whisper/.venv/bin:$PATH"
RUN pip install hailo_packages/hailort-4.20.0-cp310-cp310-linux_aarch64.whl

WORKDIR /home/wyoming_hailo_whisper/wyoming_hailo_whisper/app
RUN ./download_resources.sh

WORKDIR /home/wyoming_hailo_whisper
RUN rm -rf hailo_packages
RUN chmod +x docker-entrypoint.sh
RUN chmod +x start-hailo-example.sh

ENTRYPOINT ["./docker-entrypoint.sh"]