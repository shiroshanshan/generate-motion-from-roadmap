import os
import argparse
from angle_calculation import *

if __name__ == '__main__':
    PATH = '/home/fan/build_roadmap/rotation/'
    PATH_3DPOSE = '/home/fan/build_roadmap/3dpose/'
    dirs = os.listdir(PATH_3DPOSE)
    for files in dirs:
        position = read_files(PATH_3DPOSE, files)
        rotationlist = []
        for frame, inposition in enumerate(position):
            rotationlist.append(positions_to_rotation(inposition,frame,22))
        target_dir = PATH + files
        with open(target_dir, 'w') as f:
            write_rotation_file(f, rotationlist)
