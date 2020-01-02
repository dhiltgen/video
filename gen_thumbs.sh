#!/bin/sh

if [ $# -ne 1 ] || [ ! -d $1 ] ; then
	echo "You must specify the location to clean up thumbnails"
	exit 1
fi

echo "Cleaning up videos for $1"
for video in $(find $1 -type f | grep -v ".thumb" | grep -v keep) ; do
	# TODO some better model to filter out non-videos
        if [ ! -e ${video}.thumb ] ; then
                echo "${video} missing thumbnail - generating it"
                if ffmpeg -i ${video} -vframes 1 ${video}.jpg; then
			mv ${video}.jpg ${video}.thumb
		else
                        echo "failed to generate thumbnail"
                fi
        fi
        echo "${video} $(identify -format '%c' ${video}.thumb)"
done
