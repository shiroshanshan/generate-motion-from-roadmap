for file in /home/fan/generate-motion-from-roadmap/video/*
do
	cd /home/fan/generate-motion-from-roadmap/video_cutted/
	dir=$(basename $file .mp4)
	mkdir $dir
	time=$(ffmpeg -i ${file} 2>&1 | grep Duration | cut -d ' ' -f 4 | sed s/,//)
	echo $time
	min=${time#*:}
	min=${min%%:*}
	min=$((10#$min+1))
	sec=${time##*:}
	sec=${sec%%.*}
	for ((i=0;i<$min;i++))
	do
		start=`echo ${i}|awk '{printf("%02d",$0)}'`
		if (($i==$(($min-1)))); then
				cmd="ffmpeg -y -i /home/fan/generate-motion-from-roadmap/video/${dir}.mp4 -ss 00:$start:00 -t 00:00:$sec -c:v libx264 -c:a aac -strict experimental -b:a 128k $dir/$start.mp4"
			else
				cmd="ffmpeg -y -i /home/fan/generate-motion-from-roadmap/video/${dir}.mp4 -ss 00:$start:00 -t 00:01:00 -c:v libx264 -c:a aac -strict experimental -b:a 128k $dir/$start.mp4"
		fi
		eval $cmd
	done
done
