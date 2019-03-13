#!/bin/zsh
for file in /home/euclid/scripts/images/*
do
	pre="ffmpeg -f image2 -i " 
	pro="/%06d.jpeg -r 30 /home/euclid/scripts/video/${file##*/}.mp4"
 	cmd=${pre}${file}${pro}
	eval $cmd
done
