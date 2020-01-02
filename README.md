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
PROC=gpu
docker stop camera${CAM}-${PROC}
docker rm camera${CAM}-${PROC}
docker run -d \
	--name camera${CAM}-${PROC} \
	-v /videos/motioneye:/videos/motioneye \
	--cpus 1.5 \
	$(if [ ${PROC} = "gpu" ]; then echo "--gpus all"; fi) \
	dhiltgen/cv:${PROC} \
	/videos/motioneye/Camera${CAM}/
```

```sh
docker run --rm -it \
	-v /videos/motioneye:/videos/motioneye \
	--entrypoint gen_thumbs \
	dhiltgen/cv:cpu \
	/videos/motioneye/

```

```sh
for video in $(find . -type f | grep -v ".thumb" | grep -v keep) ; do
	if [ ! -e ${video}.thumb ] ; then
		echo "${video} missing thumbnail - generating it"
		if ffmpeg -i ${video} -vframes 1 ${video}.jpg; then
			mv ${video}.jpg ${video}.thumb 
		else
			echo "failed to generate thumbnail"
			touch ${video}.thumb 
		fi
        	if [ ! -s ${video}.thumb ] ; then
			rm -f ${video}.thumb 
			convert -size 1280x960 canvas:black ${video}.jpg
			mv ${video}.jpg ${video}.thumb 
        	fi
	fi
	echo "${video} $(identify -format '%c' ${video}.thumb)"
done
```

```sh
for video in $(find . -type f | grep -v ".thumb" | grep -v keep) ; do
	if [ ! -e ${video}.thumb ] ; then
		echo "${video} missing thumbnail - consider generating it"
		continue
	fi
	echo "${video} $(identify -format '%c' ${video}.thumb)"
done
```

Nuke empty files
```sh
for video in $(find . -type f | grep -v keep) ; do
        if [ ! -s ${video} ] ; then
                echo "${video} appears to be an empty file"
		rm -f ${video} ${video}.thumb
        fi
done
```
