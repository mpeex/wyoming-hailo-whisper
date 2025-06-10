# Hailo accelerated Whisper wrapped in a Wyoming server for Home Assistant in a Raspberry Pi 5
## [wyoming-faster-whisper]() adapted for running [Hailo speech recognition example](https://github.com/hailo-ai/Hailo-Application-Code-Examples/tree/main/runtime/hailo-8/python/speech_recognition)

*Tested on the following configuration* 
- *Rpi5 running Debian 12 (bookwork)*
- *Hailo8L (Hailo8 should work, see install section below)*
- *HA core 2024.11.3 & frontend 20241106.2 (HA OS is not tested)* 

**Prereq**

From a Rpi terminal, execute `hailortcli scan` and verify the output is similar to 
>Hailo Devices:

>[-] Device: 0001:04:00.0

**Install**

1. clone the repo and `cd` to it
2. download in `hailo_packages` folder the following packages from [Hailo Developer Zone](https://hailo.ai/developer-zone/) (requires authentication)
- hailort_4.20.0_arm64.deb
- hailort-4.20.0-cp310-cp310-linux_aarch64.whl
- hailort-pcie-driver_4.20.0_all.deb

*Might work also with 4.21 version, but it is untested*
3. build the image

`docker build  --network=host -t wyoming-hailo-whisper.img .`
4. run the image, for example:

`docker run -it -p 10600:10600 --privileged  wyoming-hailo-whisper.img:latest`
5. integrate with Home Assistant
- Add Whisper integration from Home Assistant UI
- hostname is the host where the container is running, port is 10600

*NOTE*: Hailo8L is used by default, if you want to change to Hailo8, edit `docker-entrypoint.sh` and modify the `--device` parameter (**not tested**)

**Troubleshooting**

Run the container via `docker run -it --entrypoint /bin/bash --privileged -p 10600:10600 wyoming-hailo-whisper.img:latest`, and execute `hailortcli scan`. Output should be similar to the one from the prerequisites.

Execute `./docker-entrypoint.sh` and ask something to Home Assistant's assistant, logging information will be printed at console. Edit `./docker-entrypoint.sh` to change log level to DEBUG if needed (add `--debug` flag).

`./start-hailo-example.sh` will execute the almost vanilla Hailo example, bypassing Home Assistant. Rpi5 host should be configured with Pipewire, connected to a Bluetooth microphone and the image should be executed via:`docker run -it --privileged -v /run/user/1000/pipewire-0:/tmp/pipewire-0 -p 10600:10600 --entrypoint /bin/bash wyoming-hailo-whisper.img:latest`
If everything is fine you should see 
>Press Enter to start recording, or 'q' to quit:

Talk to the bluetooth mic, the transcription will be printed at console.