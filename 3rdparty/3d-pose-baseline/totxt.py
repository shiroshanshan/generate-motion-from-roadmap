import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import tensorflow as tf
import data_utils
import viz
import re
import cameras
import json
import os
import time
import math
from predict_3dpose import create_model
import cv2
import imageio
import logging
from sklearn import neighbors
import scipy as sp
from pprint import pprint
from scipy.interpolate import interp1d
from scipy.interpolate import UnivariateSpline

FLAGS = tf.app.flags.FLAGS

order = [15, 12, 25, 26, 27, 17, 18, 19, 1, 2, 3, 6, 7, 8]
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def write_pos_data(channels, ax, posf):

    assert channels.size == len(data_utils.H36M_NAMES)*3, "channels should have 96 entries, it has %d instead" % channels.size
    vals = np.reshape( channels, (len(data_utils.H36M_NAMES), -1) )

    I   = np.array([1,2,3,1,7,8,1, 13,14,15,14,18,19,14,26,27])-1 # start points
    J   = np.array([2,3,4,7,8,9,13,14,15,16,18,19,20,26,27,28])-1 # end points
    # LR  = np.array([1,1,1,0,0,0,0, 0, 0, 0, 0, 0, 0, 1, 1, 1], dtype=bool)


    outputed = []

    # Make connection matrix
    for i in np.arange( len(I) ):
        x, y, z = [np.array( [vals[I[i], j], vals[J[i], j]] ) for j in range(3)]



        if I[i] not in outputed:

            logger.debug("I -> x={0}, y={1}, z={2}".format(x[0], y[0], z[0]))
            posf.write(str(I[i]) + " "+ str(x[0]) +" "+ str(y[0]) +" "+ str(z[0]) + ", ")
            outputed.append(I[i])


        if J[i] not in outputed:
            logger.debug("J -> x={0}, y={1}, z={2}".format(x[1], y[1], z[1]))
            posf.write(str(J[i]) + " "+ str(x[1]) +" "+ str(y[1]) +" "+ str(z[1]) + ", ")
            outputed.append(J[i])

    posf.write("\n")

#
# def take_outlier(cache):
#     difference = []
#     distance = []
#     for frame,xy in cache.items():
#         distance.append(full_body_dis(cache[frame]))
#         if frame == 0:
#             continue
#         else:
#             difference.append(full_body_dis(cache[frame])-full_body_dis(cache[frame-1]))
#     return distance, difference

# def get_replace_index(need_replaced):
#     index = []
#     for i in range(len(need_replaced)):
#         if need_replaced[i] == -1:
#             index.append(i)
#         else:
#             pass
#     return index
#
# def interpolation_replace(need_replaced,cache):
#     out_array = []
#     joint_array = []
#     joints_num = 36
#     index = get_replace_index(need_replaced)
#     for i in range(len(cache)):
#         joint_array.append(cache[i])
#     for joint in range(joints_num):
#         x = []
#         frame = []
#         for row in range(len(joint_array)):
#             if row not in index:
#                 x.append(joint_array[row][joint])
#                 frame.append(row)
#         frame_resampled = np.array(range(len(joint_array)))
#         spl = UnivariateSpline(frame, x, k=3)
#         min_x, max_x = min(x), max(x)
#         smooth_fac = max_x - min_x
#         smooth_resamp = 125
#         smooth_fac = smooth_fac * smooth_resamp
#         spl.set_smoothing_factor(float(smooth_fac))
#         xnew = spl(frame_resampled)
#         tmp = []
#         for i in range(len(xnew)):
#             if i in index:
#                 tmp.append(xnew[i])
#             else:
#                 tmp.append(joint_array[i][joint])
#         out_array.append(tmp)
#     return out_array
#
def show_anim_curves(anim_dict, _plt):
    val = np.array(list(anim_dict.values()))
    for o in range(0,36,2):
        x = val[:,o]
        y = val[:,o+1]
        _plt.plot(x, 'r--', linewidth=0.2)
        _plt.plot(y, 'g', linewidth=0.2)
    return _plt

def read_openpose_json(smooth=True, *args):
    detect = 0
    # openpose output format:
    # [x1,y1,c1,x2,y2,c2,...]
    # ignore confidence score, take x and y [x1,y1,x2,y2,...]

    logger.info("start reading openpose files")
    #load json files
    json_files = os.listdir(openpose_output_dir)
    # check for other file types
    json_files = sorted([filename for filename in json_files if filename.endswith(".json")])
    cache = {}
    smoothed = {}
    ### extract x,y and ignore confidence score
    for file_name in json_files:
        logger.debug("reading {0}".format(file_name))
        _file = os.path.join(openpose_output_dir, file_name)
        if not os.path.isfile(_file): raise Exception("No file found!!, {0}".format(_file))
        data = json.load(open(_file))
        #take first person
        _data = data["people"][0]["pose_keypoints_2d"]
        xy = []
        #ignore confidence score
        for o in range(0,len(_data),3):
            detect += 1
            #print(len(_data))
            xy.append(_data[o])
            xy.append(_data[o+1])

        # get frame index from openpose 12 padding

        frame_indx = re.split(r'[\_]+',file_name)[1]
        #add xy to frame
        cache[int(frame_indx)] = xy
    plt.figure(1)
    drop_curves_plot = show_anim_curves(cache, plt)
    pngName = 'gif_output/dirty_plot.png'
    drop_curves_plot.savefig(pngName)
    logger.info('writing gif_output/dirty_plot.png')

    # exit if no smoothing
    if not smooth:
        # return frames cache incl. 18 joints (x,y)
        return cache

    if len(json_files) == 1:
        logger.info("found single json file")
        # return frames cache incl. 18 joints (x,y) on single image\json
        return cache

    if len(json_files) <= 8:
        raise Exception("need more frames, min 9 frames/json files for smoothing!!!")

    logger.info("start smoothing")
    # ###smoothing by delect outlier
    # distance, _ = take_outlier(cache)
    # local_outlier_factor = neighbors.LocalOutlierFactor()
    # distance = np.array(distance)
    # distance = distance.reshape(len(distance),1)
    # need_replaced = local_outlier_factor.fit_predict(distance)
    # out_array = interpolation_replace(need_replaced,cache)
    # cache = joint_to_dic(out_array)
    # plt.figure(4)
    # outlier_curves_plot = show_anim_curves(cache, plt)
    # pngName = 'gif_output/outlier_plot.png'
    # outlier_curves_plot.savefig(pngName)

    # smooth by fft
    for frame, xy in cache.items():
        smoothed_list = []
        _len = len(xy)
        tmplistx = []
        tmplisty = []
        for x in range(0,_len,2):
            tmplistx.append(xy[x])
            tmplisty.append(xy[x+1])
        X = np.fft.fft(tmplistx)
        Y = np.fft.fft(tmplisty)
        N = len(tmplistx)
        fps = 30
        dt = 1./fps
        t = np.arange(0,N*dt,dt)
        freq = np.linspace(0,1./dt,N)
        fc = 20

        X = X/(N/2)
        X[0] = X[0]/2
        X2 = X.copy()
        X2[(freq > fc)] = 0
        x2 = np.fft.ifft(X2)
        x2 = np.real(x2*N)

        Y = Y/(N/2)
        Y[0] = Y[0]/2
        Y2 = Y.copy()
        Y2[(freq > fc)] = 0
        y2 = np.fft.ifft(Y2)
        y2 = np.real(y2*N)

        for x in range(18):
            smoothed_list.append(x2[x])
            smoothed_list.append(y2[x])
        smoothed[frame] = smoothed_list


    # # create frame blocks
    # head_frame_block = [int(re.split(r"[\_]+", o)[1]) for o in json_files[:4]]
    # tail_frame_block = [int(re.split(r"[\_]+", o)[1]) for o in json_files[-4:]]
    #
    # ## smooth by median filter
    # for frame, xy in cache.items():
    #
    #     # create neighbor array based on frame index
    #     forward, back = ([] for _ in range(2))
    #
    #     # joints x,y array
    #     _len = len(xy) # 36
    #     # print(len(xy))
    #
    #     # create array of parallel frames (-3<n>3)
    #     for neighbor in range(1,3):
    #         # first n frames, get value of xy in postive lookahead frames(current frame + 3)
    #         if frame in head_frame_block:
    #             forward += cache[frame+neighbor]
    #         # last n frames, get value of xy in negative lookahead frames(current frame - 3)
    #         elif frame in tail_frame_block:
    #             back += cache[frame-neighbor]
    #         else:
    #             # between frames, get value of xy in bi-directional frames(current frame -+ 3)
    #             forward += cache[frame+neighbor]
    #             back += cache[frame-neighbor]
    #
    #     # build frame range vector
    #     frames_joint_median = [0 for i in range(_len)]
    #     # more info about mapping in src/data_utils.py
    #     # for each 18joints*x,y  (x1,y1,x2,y2,...)~36
    #     for x in range(0,_len,2):
    #         # set x and y
    #         y = x+1
    #         if frame in head_frame_block:
    #             # get vector of n frames forward for x and y, incl. current frame
    #             # x_v = [xy[x], forward[x], forward[x+_len], forward[x+_len*2]]
    #             # y_v = [xy[y], forward[y], forward[y+_len], forward[y+_len*2]]
    #             x_v = [xy[x], forward[x], forward[x+_len]]
    #             y_v = [xy[y], forward[y], forward[y+_len]]
    #         elif frame in tail_frame_block:
    #             # get vector of n frames back for x and y, incl. current frame
    #             # x_v =[xy[x], back[x], back[x+_len], back[x+_len*2]]
    #             # y_v =[xy[y], back[y], back[y+_len], back[y+_len*2]]
    #             x_v =[xy[x], back[x], back[x+_len]]
    #             y_v =[xy[y], back[y], back[y+_len]]
    #         else:
    #             # get vector of n frames forward/back for x and y, incl. current frame
    #             # median value calc: find neighbor frames joint value and sorted them, use numpy median module
    #             # frame[x1,y1,[x2,y2],..]frame[x1,y1,[x2,y2],...], frame[x1,y1,[x2,y2],..]
    #             #                 ^---------------------|-------------------------^
    #             # x_v =[xy[x], forward[x], forward[x+_len], forward[x+_len*2],
    #             #         back[x], back[x+_len], back[x+_len*2]]
    #             # y_v =[xy[y], forward[y], forward[y+_len], forward[y+_len*2],
    #             #         back[y], back[y+_len], back[y+_len*2]]
    #             x_v =[xy[x], forward[x], back[x]]
    #             y_v =[xy[y], forward[y], back[y]]
    #
    #         # get median of vector
    #         x_med = np.median(sorted(x_v))
    #         y_med = np.median(sorted(y_v))
    #
    #         # holding frame drops for joint
    #         if not x_med:
    #             # allow fix from first frame
    #             if frame:
    #                 # get x from last frame
    #                 x_med = smoothed[frame-1][x]
    #         # if joint is hidden y
    #         if not y_med:
    #             # allow fix from first frame
    #             if frame:
    #                 # get y from last frame
    #                 y_med = smoothed[frame-1][y]
    #
    #         # build new array of joint x and y value
    #         frames_joint_median[x] = x_med
    #         frames_joint_median[x+1] = y_med
    #
    #     smoothed[frame] = frames_joint_median

    ##smooth by replace outlier and interpolation
    # distance, _ = take_outlier(cache)
    # local_outlier_factor = neighbors.LocalOutlierFactor()
    # distance = np.array(distance)
    # distance = distance.reshape(len(distance),1)
    # need_replaced = local_outlier_factor.fit_predict(distance)
    # out_array = interpolation_replace(need_replaced,cache)
    # for frame in range(len(out_array[0])):
    #     joints = []
    #     for joint in range(len(out_array)):
    #         joints.append(out_array[joint][frame])
    #     smoothed[frame] = joints


    return smoothed


def main(_):
    #ABS_DIR = os.path.abspath('.')
    posf = open(pose_output_dir, 'w')
    #smoothedf = open(ABS_DIR + '/tmp/smoothed.txt', 'w')

    smoothed = read_openpose_json()
    plt.figure(2)
    smooth_curves_plot = show_anim_curves(smoothed, plt)
    pngName = 'gif_output/smooth_plot.png'
    smooth_curves_plot.savefig(pngName)
    logger.info('writing gif_output/smooth_plot.png')

    if FLAGS.interpolation:
        logger.info("start interpolation")

        framerange = len( smoothed.keys() )
        joint_rows = 36
        array = np.concatenate(list(smoothed.values()))
        array_reshaped = np.reshape(array, (framerange, joint_rows) )
        print(array_reshaped[0,:])

        arm = [4,5,6,7,8,9,10,11]
        multiplier = FLAGS.multiplier
        multiplier_inv = 1/multiplier

        out_array = np.array([])
        for row in range(joint_rows):
            x = []
            for frame in range(framerange):
                x.append( array_reshaped[frame, row] )

            frame = range( framerange )
            frame_resampled = np.arange(0, framerange, multiplier)
            spl = UnivariateSpline(frame, x, k=3)
            #relative smooth factor based on jnt anim curve
            min_x, max_x = min(x), max(x)
            smooth_fac = max_x - min_x
            if row in arm:
                smooth_resamp = 1
            else:
                smooth_resamp = 75
            smooth_fac = smooth_fac * smooth_resamp
            spl.set_smoothing_factor( float(smooth_fac) )
            xnew = spl(frame_resampled)

            out_array = np.append(out_array, xnew)

        logger.info("done interpolating. reshaping {0} frames,  please wait!!".format(framerange))

        a = np.array([])
        for frame in range( int( framerange * multiplier_inv ) ):
            jnt_array = []
            for jnt in range(joint_rows):
                jnt_array.append( out_array[ jnt * int(framerange * multiplier_inv) + frame] )
            a = np.append(a, jnt_array)

        a = np.reshape(a, (int(framerange * multiplier_inv), joint_rows))
        out_array = a

        interpolate_smoothed = {}
        for frame in range( int(framerange * multiplier_inv) ):
            interpolate_smoothed[frame] = list( out_array[frame] )

        plt.figure(3)
        smoothed = interpolate_smoothed
        interpolate_curves_plot = show_anim_curves(smoothed, plt)
        pngName = 'gif_output/interpolate_{0}.png'.format(smooth_resamp)
        interpolate_curves_plot.savefig(pngName)
        logger.info('writing gif_output/interpolate_plot.png')

    enc_in = np.zeros((1, 64))
    enc_in[0] = [0 for i in range(64)]

    actions = data_utils.define_actions(FLAGS.action)

    SUBJECT_IDS = [1, 5, 6, 7, 8, 9, 11]
    rcams = cameras.load_cameras(FLAGS.cameras_path, SUBJECT_IDS)
    train_set_2d, test_set_2d, data_mean_2d, data_std_2d, dim_to_ignore_2d, dim_to_use_2d = data_utils.read_2d_predictions(
        actions, FLAGS.data_dir)
    train_set_3d, test_set_3d, data_mean_3d, data_std_3d, dim_to_ignore_3d, dim_to_use_3d, train_root_positions, test_root_positions = data_utils.read_3d_data(
        actions, FLAGS.data_dir, FLAGS.camera_frame, rcams, FLAGS.predict_14)

    device_count = {"GPU": 1}
    png_lib = []
    with tf.Session(config=tf.ConfigProto(
            device_count=device_count,
            allow_soft_placement=True)) as sess:
        #plt.figure(3)
        batch_size = 128
        model = create_model(sess, actions, batch_size)
        iter_range = len(smoothed.keys())
        for n, (frame, xy) in enumerate(smoothed.items()):
            logger.info("calc frame {0}/{1}".format(frame, iter_range))
            # map list into np array
            joints_array = np.zeros((1, 36))
            joints_array[0] = [0 for i in range(36)]
            for o in range(len(joints_array[0])):
                #feed array with xy array
                joints_array[0][o] = xy[o]
            _data = joints_array[0]
            #smoothedf.write(' '.join(map(str, _data)))
            #smoothedf.write("\n")
            # mapping all body parts or 3d-pose-baseline format
            for i in range(len(order)):
                for j in range(2):
                    # create encoder input
                    enc_in[0][order[i] * 2 + j] = _data[i * 2 + j]
            for j in range(2):
                # Hip
                enc_in[0][0 * 2 + j] = (enc_in[0][1 * 2 + j] + enc_in[0][6 * 2 + j]) / 2
                # Neck/Nose
                enc_in[0][14 * 2 + j] = (enc_in[0][15 * 2 + j] + enc_in[0][12 * 2 + j]) / 2
                # Thorax
                enc_in[0][13 * 2 + j] = 2 * enc_in[0][12 * 2 + j] - enc_in[0][14 * 2 + j]

            # set spine
            spine_x = enc_in[0][24]
            spine_y = enc_in[0][25]

            enc_in = enc_in[:, dim_to_use_2d]
            mu = data_mean_2d[dim_to_use_2d]
            stddev = data_std_2d[dim_to_use_2d]
            enc_in = np.divide((enc_in - mu), stddev)

            dp = 1.0
            dec_out = np.zeros((1, 48))
            dec_out[0] = [0 for i in range(48)]
            _, _, poses3d = model.step(sess, enc_in, dec_out, dp, isTraining=False)
            all_poses_3d = []
            enc_in = data_utils.unNormalizeData(enc_in, data_mean_2d, data_std_2d, dim_to_ignore_2d)
            poses3d = data_utils.unNormalizeData(poses3d, data_mean_3d, data_std_3d, dim_to_ignore_3d)
            gs1 = gridspec.GridSpec(1, 1)
            gs1.update(wspace=-0.00, hspace=0.05)  # set the spacing between axes.
            plt.axis('off')
            all_poses_3d.append( poses3d )
            enc_in, poses3d = map( np.vstack, [enc_in, all_poses_3d] )
            subplot_idx, exidx = 1, 1
            _max = 0
            _min = 10000

            for i in range(poses3d.shape[0]):
                for j in range(32):
                    tmp = poses3d[i][j * 3 + 2]
                    poses3d[i][j * 3 + 2] = poses3d[i][j * 3 + 1]
                    poses3d[i][j * 3 + 1] = tmp
                    if poses3d[i][j * 3 + 2] > _max:
                        _max = poses3d[i][j * 3 + 2]
                    if poses3d[i][j * 3 + 2] < _min:
                        _min = poses3d[i][j * 3 + 2]

            for i in range(poses3d.shape[0]):
                for j in range(32):
                    poses3d[i][j * 3 + 2] = _max - poses3d[i][j * 3 + 2] + _min
                    poses3d[i][j * 3] += (spine_x - 630)
                    poses3d[i][j * 3 + 2] += (500 - spine_y)

            # Plot 3d predictions
            ax = plt.subplot(gs1[subplot_idx - 1], projection='3d')
            ax.view_init(18, -70)
            if np.min(poses3d) < -1000:
                try:
                    poses3d = before_pose
                except:
                    pass

            p3d = poses3d
            #viz.show3Dpose(p3d, ax, lcolor="#9b59b6", rcolor="#2ecc71")

            # pngName = 'png/pose_frame_{0}.png'.format(str(frame).zfill(12))
            # plt.savefig(pngName)
            # if FLAGS.write_gif:
            #     png_lib.append(imageio.imread(pngName))
            before_pose = poses3d
            write_pos_data(poses3d, ax, posf)
        posf.close()
    #
    # if FLAGS.write_gif:
    #     if FLAGS.interpolation:
    #         #take every frame on gif_fps * multiplier_inv
    #         png_lib = np.array([png_lib[png_image] for png_image in range(0,len(png_lib), int(multiplier_inv)) ])
    #     logger.info("creating Gif png/animation.gif, please Wait!")
    #     imageio.mimsave('gif_output/animation.gif', png_lib, fps=FLAGS.gif_fps)
    # logger.info("Done!".format(pngName))


if __name__ == "__main__":

    openpose_output_dir = FLAGS.openpose
    pose_output_dir = FLAGS.pose

    level = {0:logging.ERROR,
             1:logging.WARNING,
             2:logging.INFO,
             3:logging.DEBUG}

    logger.setLevel(level[FLAGS.verbose])


    tf.app.run()
