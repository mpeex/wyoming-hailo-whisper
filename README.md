# Hailo Whisper model in a Wyoming server for Home Assistant 
### A quick conversion of [wyoming-faster-whisper](https://github.com/rhasspy/wyoming-faster-whisper) to run [Hailo Whisper model](https://github.com/hailo-ai/Hailo-Application-Code-Examples/tree/main/runtime/hailo-8/python/speech_recognition)

*Tested on the following configuration* 
- *Rpi5 running Debian 12 (bookworm)*
- *Hailo8L (Hailo8 should work, see install section below)*
- *HailoRT version 4.21*
- *HA Container installation (HA core 2024.11.3, HA frontend 20241106.2)*

**UPDATE: a user reported success in creating an HassOS AddOn, please see section at the bottom of the page for instructions** 

**Prereq**

From a Rpi terminal, execute `hailortcli -version`. Depending on the version:

If v4.21, skip to the next section.

If v4.20:
- consider an upgrade using [Hailo's guide](https://hailo.ai/developer-zone/documentation/hailort-v4-21-0/?sp_referrer=install/install.html#ubuntu-installation)
- change the Dockerfile according to v4.20 packages (see Dockerfile_experiments)

**Install**

1. clone the repo and `cd` to it. Hailo8L is the default, if you want to change to Hailo8, edit `docker-entrypoint.sh` and modify the `--device` parameter accordingly (**not tested**)

2. `mkdir hailo_packages` and download in it the following packages from [Hailo Developer Zone](https://hailo.ai/developer-zone/) (requires authentication, filter with HailoRT/ARM64/Linux/Python3.10)

*HailoRT version 4.21* 
- hailort_4.21.0_arm64.deb
- hailort-4.21.0-cp310-cp310-linux_aarch64.whl

*If you want to use HailoRT version 4.20*
- hailort_4.20.0_arm64.deb
- hailort-4.20.0-cp310-cp310-linux_aarch64.whl
- use/edit `Dockerfile_experiments`

3. build the image

`docker build  --network=host -t wyoming-hailo-whisper.img .`

4. run the image, for example:

`docker run -it -p 10600:10600 --privileged  wyoming-hailo-whisper.img:latest`

5. integrate with Home Assistant
- add Whisper integration from Home Assistant UI
- hostname is the host where the container is running, port is 10600
- configure HA voice assistant to use `wyoming-hailo-whisper`

6. If everything works fine, automate the container execution using `compose.yaml` using portainer or similar.

**Troubleshooting**

Run the container via `docker run -it --entrypoint /bin/bash --privileged wyoming-hailo-whisper.img:latest`. Execute `./docker-entrypoint.sh` and ask something to Home Assistant's voice assistant, logging information will be printed at console. Edit `./docker-entrypoint.sh` to change log level to DEBUG if needed (add `--debug` flag).

**Experiment with a Bluetooth audio source**

Rpi5 host should be configured with Pipewire and connected to a Bluetooth microphone.

Rebuild the image with the additional libraries for Pipewire, Alsa, Bluetooth (see Dockerfile_experiments).

Start the image via:`docker run -it --privileged -v /run/user/1000/pipewire-0:/tmp/pipewire-0 -p 10600:10600 --entrypoint /bin/bash wyoming-hailo-whisper.img:latest`

`./start-hailo-example.sh` will execute the almost vanilla Hailo example, bypassing Home Assistant and Wyoming.  

If everything is fine you should see 
>Press Enter to start recording, or 'q' to quit:

Press Enter and speak via the bluetooth mic, the transcription will be printed at console.

**HassOS users**

The following steps has been proven successfull by a user to generate an HA AddOn.
Familiarize yourself with the [HA AddOn official guide](https://developers.home-assistant.io/docs/add-ons/tutorial)
1. SSH to your HA machine and go to the `/addons` folder
2. Create a new directory called `wyoming-hailo-whisper`
3. Copy inside `wyoming-hailo-whisper` directory the entire repo content (including `hailo_packages` that has to be manually created, see installation steps 1 and 2 above)
4. Rename `Dockerfile_HassOS_AddOn` to `Dockerfile`
5. The default is to use Hailo8L, if you need Hailo8 edit the `--device` parameter in `run.sh` accordingly 
5. Proceed from now on with [HA AddOn official guide, step 2](https://developers.home-assistant.io/docs/add-ons/tutorial#step-2-installing-and-testing-your-add-on)

