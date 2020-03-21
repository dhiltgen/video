#!/bin/bash

# Script to be able to keep the obj detection filtering containers running

MAX_GPU=2

# Start up the thumb generator in the background
ID=$(docker run --rm -d \
	-v /videos/motioneye:/videos/motioneye \
	--entrypoint gen_thumbs \
	dhiltgen/cv:cpu \
	/videos/motioneye/ )

RUNNING_GPU=( $(docker ps --filter name=camera --format '{{.Names}}' | sort | grep -- '-gpu') )
RUNNING_CPU=( $(docker ps --filter name=camera --format '{{.Names}}' | sort | grep -- '-cpu') )
AVAILABLE_GPU=( $(docker ps -a --filter name=camera --format '{{.Names}}' | sort | grep -- '-gpu') )
AVAILABLE_CPU=( $(docker ps -a --filter name=camera --format '{{.Names}}' | sort | grep -- '-cpu') )

CAMERAS=( $(for cam in ${AVAILABLE_GPU[@]}; do echo $cam|cut -f1 -d-; done | sort -R -u) )
NOT_RUNNING=( )

#echo "Cameras: ${CAMERAS[@]}"
#echo "Running GPU: ${RUNNING_GPU[@]}"
#echo "Running CPU: ${RUNNING_CPU[@]}"
#echo "Available GPU: ${AVAILABLE_GPU[@]}"
#echo "Available CPU: ${AVAILABLE_CPU[@]}"

# Return 0 if the camera is running, non-zero if it's not running on CPU or GPU
function isRunning {
	echo ${RUNNING_GPU[@]} | grep $1 > /dev/null && return 0
	echo ${RUNNING_CPU[@]} | grep $1 > /dev/null && return 0
	return 1
}

for cam in ${CAMERAS[@]}; do
	if ! isRunning ${cam}; then
		NOT_RUNNING+=(${cam})
	fi
done

# Wait for the thumb generator
docker wait ${ID}

if [ ${#NOT_RUNNING[@]} -eq 0 ]; then
	echo "All filters running"
	exit 0
fi


# Restart those not running, favoring GPU
echo "Restarting: ${NOT_RUNNING[@]}"
for cam in ${NOT_RUNNING[@]}; do
	if [ ${#RUNNING_GPU[@]} -lt ${MAX_GPU} ]; then
		docker start ${cam}-gpu 
		RUNNING_GPU+=(${cam}-gpu)
	else
		docker start ${cam}-cpu
		RUNNING_CPU+=(${cam}-cpu)
	fi
done


