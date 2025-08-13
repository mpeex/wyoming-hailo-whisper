
FROM ubuntu:22.04
#FROM ghcr.io/home-assistant/aarch64-base-ubuntu:20.04
#FROM ghcr.io/hassio-addons/ubuntu-base/aarch64:8e1f32f
ARG S6_OVERLAY_VERSION=3.2.1.0
ARG BASHIO_VERSION=0.17.1

RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone
ARG DEBIAN_FRONTEND=noninteractive

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
    xz-utils \
    curl

ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-aarch64.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-aarch64.tar.xz

RUN mkdir -p /usr/src/bashio \
    && curl -L -f -s "https://github.com/hassio-addons/bashio/archive/v${BASHIO_VERSION}.tar.gz" \
        | tar -xzf - --strip 1 -C /usr/src/bashio \
    && mv /usr/src/bashio/lib /usr/lib/bashio \
    && ln -s /usr/lib/bashio/bashio /usr/bin/bashio \
    && rm -rf /usr/src/*


RUN dpkg --unpack hailo_packages/hailort_4.21.0_arm64.deb 

RUN script/setup && script/package
ENV PATH="/home/wyoming_hailo_whisper/.venv/bin:$PATH"
RUN pip install hailo_packages/hailort-4.21.0-cp310-cp310-linux_aarch64.whl

RUN rm -rf hailo_packages

WORKDIR /home/wyoming_hailo_whisper/wyoming_hailo_whisper/app
RUN ./download_resources.sh

#WORKDIR /home/wyoming_hailo_whisper
#RUN rm -rf hailo_packages
RUN chmod a+x /run.sh

ENTRYPOINT ["/init"]
CMD ["/run.sh"]
