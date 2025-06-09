docker build  --network=host -t wyoming-hailo-whisper.img .
docker run -it -p 10600:10600 --privileged  wyoming-hailo-whisper.img:latest
