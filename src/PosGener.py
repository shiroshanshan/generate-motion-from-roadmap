import os
import re
import argparse
from check import openpose_select

def process(PATH, folder, file):
    try:
        """
        process by openpose
        """
        os.chdir(openpose)
        os.popen('/build/examples/openpose/openpose.bin --video {0}/{1}/{2} \
        --write_json {3}/openpose/{1}/{4}/ --display 0 --render_pose 0 \
        --model_pose COCO'.format(INPUT, folder, file, PATH, file.split('.')[0])).readlines()

        print('################ openpose end #####################')

        """
        remove abnormal data
        """
        result = openpose_select('{0}/openpose/{1}/{2}/'.format(PATH, folder, file.split('.')[0]))
        print('select check: '+result)
        if re.split(r'[\s]+', result)[0] == 'error':
            return result

        """
        resampling and 3d pose estimation
        """
        os.chdir(POSE)
        os.popen('python {0}/src/totxt.py --pose {1}/3dpose/{2}{3}.txt --openpose {1}/openpose/{2}/{3}/ \
        --interpolation --multiplier 1'.format(POSE, PATH, folder, file.split('.')[0])).readlines()
        print('################ totxt end #####################')

        return 'success'
    except:
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='extract motion from video to joint position')
    parser.add_argument('-i', '--input', dest='input', type=str,
                        help='where the video files is saved')
    parser.add_argument('-o', '--openpose', dest='openpose', type=str,
                        help='where your openpose is installed')
    parser.add_argument('-p', '--pose', dest='pose', type=str,
                        help='where your 3d pose estimation is installed')
    args = parser.parse_args()

    INPUT = args.input
    OPENPOSE = args.openpose
    POSE = args.post
    PATH = os.getcwd()
    dirs = os.listdir(INPUT)

    for folder in dirs:
        files = os.listdir('{0}/{1}'.format(INPUT, folder))
        os.mkdir('{0}/openpose/{1}'.format(INPUT, folder))
        for file in files:
            get_result = process(PATH, folder, file)
            print(get_result)
