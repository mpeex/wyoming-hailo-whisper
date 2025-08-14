
FROM ubuntu:22.04

# Default ENV
ENV \
    LANG="C.UTF-8" \
    DEBIAN_FRONTEND="noninteractive" \
    S6_BEHAVIOUR_IF_STAGE2_FAILS=2 \
    S6_CMD_WAIT_FOR_SERVICES_MAXTIME=0 \
    S6_CMD_WAIT_FOR_SERVICES=1 \
    S6_SERVICES_READYTIME=50

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Build args
ARG S6_OVERLAY_VERSION=3.2.1.0
ARG BASHIO_VERSION=0.17.1
ARG TEMPIO_VERSION=2024.11.2

# Base system
WORKDIR /usr/src

RUN \
    set -x \
    && apt-get update && apt-get install -y --no-install-recommends \
        bash \
        jq \
        tzdata \
        curl \
        ca-certificates \
        xz-utils \
    \
    && curl -L -f -s "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-aarch64.tar.xz" \
        | tar Jxvf - -C / \
    && curl -L -f -s "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz" \
        | tar Jxvf - -C / \
    && curl -L -f -s "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-symlinks-arch.tar.xz" \
        | tar Jxvf - -C / \
    && curl -L -f -s "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-symlinks-noarch.tar.xz" \
        | tar Jxvf - -C / \
    && mkdir -p /etc/fix-attrs.d \
    && mkdir -p /etc/services.d \
    \
    && curl -L -f -s -o /usr/bin/tempio \
        "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_aarch64" \
    && chmod a+x /usr/bin/tempio \
    \
    && mkdir -p /usr/src/bashio \
    && curl -L -f -s "https://github.com/hassio-addons/bashio/archive/v${BASHIO_VERSION}.tar.gz" \
        | tar -xzf - --strip 1 -C /usr/src/bashio \
    && mv /usr/src/bashio/lib /usr/lib/bashio \
    && ln -s /usr/lib/bashio/bashio /usr/bin/bashio \
    \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/src/*


RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone

RUN mkdir /home/wyoming_hailo_whisper
WORKDIR /home/wyoming_hailo_whisper

COPY ./hailo_packages/hailort-4.21.0-cp310-cp310-linux_aarch64.whl ./hailo_packages/
COPY ./hailo_packages/hailort_4.21.0_arm64.deb ./hailo_packages/
COPY ./script/ ./script/
COPY ./wyoming_hailo_whisper/ ./wyoming_hailo_whisper/
COPY ./requirements.txt ./
COPY ./run.sh /
COPY ./setup.* ./

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    ffmpeg \
    libportaudio2 \
    wget \
    nano

RUN dpkg --unpack hailo_packages/hailort_4.21.0_arm64.deb 

RUN script/setup && script/package
ENV PATH="/home/wyoming_hailo_whisper/.venv/bin:$PATH"
RUN pip install hailo_packages/hailort-4.21.0-cp310-cp310-linux_aarch64.whl

RUN rm -rf hailo_packages

WORKDIR /home/wyoming_hailo_whisper/wyoming_hailo_whisper/app
RUN ./download_resources.sh

RUN chmod a+x /run.sh

# S6-Overlay
WORKDIR /
ENTRYPOINT ["/init"]
CMD ["/run.sh"]
