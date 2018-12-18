# generate-motion-from-roadmap
Let's interact with virtual agent in the screen. Here's some procedure of how to create a roadmap and how to run this system.

the structure of how input video is saved

dependency openpose 3dposebaseline flask openface

this file structure

we need to cut video into segment before create roadmap the simplest way is to run ./script/convert_video_per_min.sh but some parameter need to be changed by yourself

data process[image] first run python src/PosGener.py -i {$VIDEO_PATH} -o {$PATH_TO_OPENPOSE} -p{PATH_TO_3d_POSE_BASELINE} to extract joint position from videos this process will take some times the output of openpose will be located in ./openpsoe and the output of 3d pose estimation will be located in ./3dpose

then run python src/AngleCalculor.py (default x-correction is 15, you can change it by your self) to convert joint position to joint angle

create roadmap[link][image] here we can create a roadmap by run python src/gene_raodmap.py to create a roadmap hierachical resampling[link] will a lot of time, and you can change batch size by yourself.

before start the server we need to run python scripts/create_routes.py to initialize the roadmap/saved/routes.json file

and here we can start the server by python server/server.py

here's some introduction about scripts and plots /scripts/clear_output.py is used to clear all of the output of runtime /scripts/txt2csv.py is used to save joint angle as csv file /plot/plot_graphs.py is used to plot the relationship between dp and dv /plot/animation.py is used to plot animation of readed data (decrease the dimension to 2)
