import sys
import os
PATH = os.getcwd()
sys.path.append('{0}/src'.format(PATH))
from ReadRoadmap import *
from flask import Flask, render_template, g, request, send_file
import pandas as pd
import datetime
import json
from gaze_deter import gaze_determinator
import logging


app = Flask(__name__)

# b = Blueprint("b", __name__)
fname = None
fv = 0
fc = 0
rdp.read_roadmap(roadmap, states, routes, routes_dic)
bone_csv_file = '{0}/model.csv'.format(PATH)
# app.register_blueprint(b)

@app.route("/")
def index():
    return render_template('betterone.html')

@app.route("/initate", methods=['GET'])
def initate():
    rdp.save_every_ten()
    global last_state
    init_state = rdp.init_state()
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    vmd_file = '{0}/server/static/vmd/{1}.vmd'.format(PATH, timenow)
    last_state = rdp.motion_generation(init_state, vmd_file, bone_csv_file, False, False)
    return timenow

@app.route("/gene_motion", methods=['GET'])
def gene_motion():
    global last_state
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    vmd_file = '{0}/server/static/vmd/{1}.vmd'.format(PATH, timenow)
    last_state = rdp.motion_generation(last_state, vmd_file, bone_csv_file, False, False)
    return timenow

@app.route("/download", methods=['POST'])
def download():
    print(request.json)
    res = request.json['time']
    download_file_name = res +'.vmd'
    download_file = '{0}/server/static/vmd/{1}.vmd'.format(PATH, res)
    return send_file(download_file, as_attachment = True, attachment_filename = download_file_name, mimetype = 'application/vocaltec-media-desc')

@app.route('/openface', methods=['POST'])
def openface():
    global fname, fv, fc
    gaze = {}
    au = {}
    happiness, sadness, surprise, fear, anger, disgust, contempt = 0, 0, 0, 0, 0, 0, 0

    Imgfile = request.files['data']
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    Imgfile.save('{0}/server/static/input/{1}.jpeg'.format(PATH, timenow))

    os.popen('~/OpenFace/build/bin/FaceLandmarkImg -f {0}/server/static/input/{1}.jpeg\
              -out_dir {0}/server/static/output/{1}'.format(PATH, timenow)).readlines()
    try:
        df = pd.read_csv('{0}/server/static/output/{1}/{1}.csv'.format(PATH, timenow), sep=',')
    except:
        print('gaze detection: no human face detected')
        return 'no gaze detected'

    #emotion recognition from action units
    au_r = df[[' AU01_r', ' AU02_r', ' AU04_r', ' AU05_r', ' AU06_r', ' AU07_r',\
     ' AU12_r', ' AU15_r', ' AU20_r', ' AU23_r', ' AU26_r']]
    au_c = df[[' AU01_c', ' AU02_c', ' AU04_c', ' AU05_c', ' AU06_c', ' AU07_c',\
     ' AU12_c', ' AU15_c', ' AU20_c', ' AU23_c', ' AU26_c']]
    # au['AU01_r'] = value

    value = df[[' gaze_0_x', ' gaze_0_y', ' gaze_0_z', ' gaze_1_x', ' gaze_1_y', ' gaze_1_z']].values
    gaze['left_eye'] = value[0][:3]
    gaze['right_eye'] = value[0][3:]
    looking = gaze_determinator(gaze)
    if looking:
        print('gaze detection: gaze detected')
    else:
        print('gaze detection: no gaze detected')

    if fname != request.form['fname']:
        if fname != None:
            tmp_key = rdp.init_states_stack.pop(0)
            tmp_value = rdp.routes_stack.pop(0)
            tmp_connects = [x[:40] for x in rdp.routes_dic[tmp_key]]
            if tmp_key in tmp_connects:
                k = tmp_connects.index(tmp_key)
                rdp.routes_dic[tmp_key][k][40] += fv
                rdp.routes_dic[tmp_key][k][41] += fc
            else:
                rdp.routes_dic[tmp_key].append(tmp_value + [fv, fc])
        fname = request.form['fname']
        fc = 1
        fv = looking
    else:
        fc += 1
        fv += looking

    return 'finished'

if __name__ == "__main__":
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.jinja_env.auto_reload = True
    app.run(host='0.0.0.0', debug=True, port=5001, ssl_context='adhoc')
    # app.run(port=8008, debug=True)
