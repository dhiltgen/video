# cv
Image detection tools for security cameras

At the moment, this has a very rudimentary python script that leverages
[Darknet Yolo](https://github.com/pjreddie/darknet) and opencv to process
one or more videos and figure out if any objects are detected.  This is
pacaged to run as a Docker Container to make it a little easier to get
all the bits and pieces built on various systems.


## Example usage

```sh
docker build -t dhiltgen/cv:cuda .
```

```sh
CAM=1
docker stop camera${CAM}-gpu
docker rm camera${CAM}-gpu
docker run -d \
	--name camera${CAM}-gpu \
	-v /videos/motioneye:/videos/motioneye \
	--gpus all \
	dhiltgen/cv:cuda \
	/videos/motioneye/Camera${CAM}
```
