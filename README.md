# cv
Image detection tools for security cameras

At the moment, this has a very rudimentary python script that leverages
[Darknet Yolo](https://github.com/pjreddie/darknet) and opencv to process
one or more videos and figure out if any objects are detected.  This is
pacaged to run as a Docker Container to make it a little easier to get
all the bits and pieces built on various systems.

## Example Video

Here's an example video that was detected by this utility from the driveway
camera at our cabin in Lake Tahoe

[![Watch the video](https://img.youtube.com/vi/d2gZbQDvtwo/hqdefault.jpg)](https://youtu.be/d2gZbQDvtwo)


## Example usage

```sh
docker build -t dhiltgen/cv:cuda .
```

```sh
INST=1
PROC=gpu
docker stop camera${INST}-${PROC}
docker rm camera${INST}-${PROC}
docker run -d \
	--name camera${INST}-${PROC} \
	-v /videos/motioneye:/videos/motioneye \
	--cpus 0.25 \
	--restart always \
	$(if [ ${PROC} = "gpu" ]; then echo "--gpus all"; fi) \
	dhiltgen/cv:${PROC} \
	/videos/motioneye/
```

```sh
docker run --rm -it \
	-v /videos/motioneye:/videos/motioneye \
	--entrypoint gen_thumbs \
	dhiltgen/cv:cpu \
	/videos/motioneye/

```
