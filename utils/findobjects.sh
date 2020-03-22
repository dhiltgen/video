#!/bin/sh

# Simple script to scan through all the clips in "." looking for 
# a specific object

for video in $(find . -type f | grep -v ".thumb" | grep -v ".keep") ; do
	if [ ! -e ${video}.thumb ] ; then
		continue
	fi
	detected=$(identify -format '%c' ${video}.thumb | grep "Objects Detected" | sed -e 's/Objects Detected:\(.*\)$/\1/g')
	if echo "${detected}" | grep $1 > /dev/null ; then
		echo "${video} ${detected}"
	fi
done
