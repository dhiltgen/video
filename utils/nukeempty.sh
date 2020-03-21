#!/bin/sh

for video in $(find . -type f | grep -v ".thumb" | grep -v ".keep") ; do
	
        if [ ! -s ${video} ] ; then
                echo "${video} is an empty file, removing"
		rm -f ${video} ${video}.thumb
        fi
done
