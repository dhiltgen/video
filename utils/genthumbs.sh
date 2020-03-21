#!/bin/sh
for video in $(find . -type f | grep -v ".thumb" | grep -v ".keep") ; do
	if [ ! -e ${video}.thumb ] ; then
		echo "${video} missing thumbnail - generating it"
		if ! ffmpeg -i ${video} -f mjpeg -vframes 1 -ss 4 -y ${video}.thumb; then
			echo "failed to generate thumbnail"
			continue
		fi
	fi
	echo "${video} $(identify -format '%c' ${video}.thumb)"
done
