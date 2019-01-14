# Generate-motion-from-roadmap
Let's interact with virtual agent in the screen. Here's some procedure of how to create a roadmap and how to run this system.

## Dependency
* [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose)
* [3DPoseBaseline](https://github.com/una-dinosauria/3d-pose-baseline)
* [Flask](http://flask.pocoo.org/)
* [OpenFace](https://github.com/TadasBaltrusaitis/OpenFace)

## Preprocess

We need to cut video into segment before create roadmap the simplest way is to run (some parameter need to be changed by yourself)
```
./script/convert_video_per_min.sh
```

## Data process
<p align="center">
    <img src="/plot/intro/preprocess.jpg", width="640">
</p>

First run ```python src/PosGener.py -i {$VIDEO_PATH} -o {$PATH_TO_OPENPOSE} -p{PATH_TO_3d_POSE_BASELINE}``` to extract joint position from videos, this process will take some times and the output of openpose will be located in ```./openpsoe``` and the output of 3d pose estimation will be located in ```./3dpose```.

Then run ```python src/AngleCalculor.py``` (default x-correction is 15, you can change it by your self) to calculate joint angle from joint position.

## Create roadmap
<p align="center">
    <img src="/plot/intro/flowchart.jpg", width="640">
</p>

Here we can create a roadmap by run ```python src/gene_raodmap.py``` to create a roadmap. Hierachical resampling will a lot of time, and you can change batch size and other parameters by yourself.

<p align="center">
    <img src="/plot/intro/anim.gif", width="320">
</p>

Before start the server we need to run ```python scripts/create_routes.py``` to initialize the ```roadmap/saved/routes.json``` file.

And here we can start the server by run ```python server/server.py```.

Here's some introduction about scripts and plots.  
* ```/scripts/clear_output.py``` is used to clear all of the output of runtime.
* ```/scripts/txt2csv.py``` is used to save joint angle as csv file.
*  ```/plot/plot_graphs.py``` is used to plot the relationship between dp and dv. 
*  ```/plot/animation.py``` is used to plot animation of readed data (decrease the dimension to 2).

## Document
click <a href='/plot/intro/roadmap_summary.pdf' target='_blank'>this</a> to open
