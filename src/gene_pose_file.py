import os
import re
from opcheck import openpose_check, openpose_select

def process(PATH, files):

    os.chdir('/home/fan/openpose')
    print('/home/fan/openpose/build/examples/openpose/openpose.bin --video ' + PATH + 'video/' + files + ' --write_json ' + PATH + 'openpose/' + files.split('.')[0] + '/ --display 0 --render_pose 0 --model_pose COCO')
    os.popen('/home/fan/openpose/build/examples/openpose/openpose.bin --video ' + PATH + 'video/' + files + ' --write_json ' + PATH + 'openpose/' + files.split('.')[0] + '/ --display 0 --render_pose 0 --model_pose COCO').readlines()
    print('################ openpose end #####################')

    result = openpose_select(PATH + 'openpose/' + files.split('.')[0] + '/')
    print('select check: '+result)
    if re.split(r'[\s]+',result)[0] == 'error':
        return result
    result = openpose_check(PATH + 'openpose/' + files.split('.')[0] + '/')
    print('check check: '+result)
    if re.split(r'[\s]+',result)[0] == 'error':
        return result

    os.popen('cd ~/3d-pose-baseline-master/').readlines()
    os.chdir('/home/fan/3d-pose-baseline-master/')
    os.popen('python /home/fan/3d-pose-baseline-master/src/totxt.py --pose ' + '/home/fan/build_roadmap/3dpose/' + files.split('.')[0] + '.txt --openpose ' + PATH + 'openpose/' + files.split('.')[0] + '/ --interpolation --multiplier 1').readlines()
    # os.popen('cd /home/fan/Documents/3dpose/output').readlines()
    print('################ totxt end #####################')

    return('success')


if __name__ == '__main__':
    PATH = '/home/fan/build_roadmap/'
    PATH_VIDEO = '/home/fan/build_roadmap/video'
    dirs = os.listdir(PATH_VIDEO)

    for files in dirs:
        get_result = process(PATH, files)
        print(get_result)
