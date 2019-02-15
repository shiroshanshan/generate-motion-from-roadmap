import sys
import os
import pandas as pd
import datetime
import json
import logging
import argparse
PATH = os.getcwd()
sys.path.append('{0}/src'.format(PATH))
from EmoReco import *
from ReadRoadmap import *
from GazeDeter import *
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

fname, gv, gc, ev, ec = None, 0, 0, 0, 0
rdp.read_roadmap(roadmap, states, routes, routes_dic)
bone_csv_file = '{0}/model.csv'.format(PATH)

@app.route("/")
def index():
    return render_template('miku.html')

@app.route("/initate", methods=['GET'])
def initate():
    rdp.save_every_ten()
    global last_state
    init_state = rdp.init_state()
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    vmd_file = '{0}/server/static/vmd/{1}.vmd'.format(PATH, timenow)
    last_state, proportion = rdp.motion_generation(init_state, vmd_file, bone_csv_file, plot, write)
    return json.dumps({'timenow': timenow, 'proportion': proportion})

@app.route("/gene_motion", methods=['GET'])
def gene_motion():
    global last_state
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    vmd_file = '{0}/server/static/vmd/{1}.vmd'.format(PATH, timenow)
    last_state, proportion = rdp.motion_generation(last_state, vmd_file, bone_csv_file, plot, write)
    return json.dumps({'timenow': timenow, 'proportion': proportion})

@app.route("/download", methods=['POST'])
def download():
    print(request.json)
    res = request.json['time']
    download_file_name = res +'.vmd'
    download_file = '{0}/server/static/vmd/{1}.vmd'.format(PATH, res)
    return send_file(download_file, as_attachment = True, attachment_filename = download_file_name, mimetype = 'application/vocaltec-media-desc')

@app.route('/openface', methods=['POST'])
def openface():
    global fname, gv, gc, ev, ec
    gaze = {}

    Imgfile = request.files['data']
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    Imgfile.save('{0}/server/static/input/{1}.jpeg'.format(PATH, timenow))

    os.popen('~/OpenFace/build/bin/FaceLandmarkImg -f {0}/server/static/input/{1}.jpeg\
              -out_dir {0}/server/static/output/{1}'.format(PATH, timenow)).readlines()
    try:
        df = pd.read_csv('{0}/server/static/output/{1}/{1}.csv'.format(PATH, timenow), sep=',')
    except:
        print('gaze detection: no human face detected')
        return json.dumps({'gaze': 'none', 'emotion': 'none'})

    #emotion recognition from action units
    EMOTION = ['anger', 'contempt', 'disgust', 'fear', 'happy', 'sadness', 'surprise', 'unsure']
    AU = [' AU01_c', ' AU02_c', ' AU04_c', ' AU05_c', ' AU06_c', ' AU07_c', ' AU09_c', ' AU10_c', ' AU12_c', ' AU15_c'\
    , ' AU17_c', ' AU20_c', ' AU23_c', ' AU26_c']
    au = df[AU].values[0]
    au = [i for i in range(len(au)) if int(au[i]) == 1]
    emotion = lcs.predict(au)
    if emotion == -1:
        print('emotion recognition: no emotion detected')
    else:
        print('emotion detection: {0}'.format(EMOTION[emotion]))
    happy = 1 if emotion == 4 else 0

    GAZE = [' gaze_0_x', ' gaze_0_y', ' gaze_0_z', ' gaze_1_x', ' gaze_1_y', ' gaze_1_z']
    value = df[GAZE].values[0]
    gaze['left_eye'] = value[:3]
    gaze['right_eye'] = value[3:]

    looking = gazedeter.deter(gaze)
    if looking:
        print('gaze detection: gaze detected')
    else:
        print('gaze detection: no gaze detected')

    if fname != request.form['fname']:
        #write if motion change
        if fname != None:
            tmp_key = rdp.init_states_stack.pop(0)
            tmp_value = rdp.routes_stack.pop(0)
            tmp_connects = [x[:40] for x in rdp.routes_dic[tmp_key]]
            if tmp_key in tmp_connects:
                k = tmp_connects.index(tmp_key)
                rdp.routes_dic[tmp_key][k][40] += gv
                rdp.routes_dic[tmp_key][k][41] += gc
                rdp.routes_dic[tmp_key][k][42] += ev
                rdp.routes_dic[tmp_key][k][43] += ec
            else:
                rdp.routes_dic[tmp_key].append(tmp_value + [gv, gc, ev, ec])
        #update motion name and accumulate
        fname = request.form['fname']
        gc, gv, ec, ev = 1, looking, 1, happy
    else:
        #accumulate if motion not change
        gc += 1
        gv += looking
        ec += 1
        ev += happy

    return json.dumps({'gaze': 'detected', 'emotion': EMOTION[emotion]}) \
    if looking else json.dumps({'gaze': 'not detected', 'emotion': EMOTION[emotion]})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='flask server for interaction system')
    parser.add_argument('-p', '--plot', dest='plot', type=bool,
                        default=False, help='plot sampled routes')
    parser.add_argument('-w', '--write', dest='write', type=bool,
                        default=False, help='log sampled routes')
    args = parser.parse_args()
    write = args.write
    plot = args.plot

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.jinja_env.auto_reload = True
    # app.run(host='0.0.0.0', debug=False, port=5001, ssl_context='adhoc', threaded=False, processes=3)
    app.run(host='0.0.0.0', debug=True, port=5001, ssl_context='adhoc', threaded=True)
