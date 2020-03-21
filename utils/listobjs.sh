#!/bin/sh

for video in $(find . -type f | grep -v ".thumb" | grep -v ".keep") ; do
	if [ ! -e ${video}.thumb ] ; then
		echo "${video} missing thumbnail - consider generating it"
		continue
	fi
	echo "${video} $(identify -format '%c' ${video}.thumb)"
done
