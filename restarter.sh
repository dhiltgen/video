#!/bin/bash

# Start up the thumb generator 
docker run --rm \
	-v /videos/motioneye:/videos/motioneye \
	--entrypoint gen_thumbs \
	dhiltgen/cv:cpu \
	/videos/motioneye/
