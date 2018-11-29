import sys
sys.path.append('/home/fan/generate-motion-from-roadmap/src')
from read_roadmap import *
from flask import Flask, render_template, g, current_app, Blueprint, request
from werkzeug.local import LocalProxy
import pandas as pd
import datetime
import os
import json

app = Flask(__name__)

# b = Blueprint("b", __name__)
fname = None
fv = 0
fc = 0
rdp.read_roadmap(roadmap, roadmap_dic)
rdp.save_every_ten()
bone_csv_file = '/home/fan/generate-motion-from-roadmap/model.csv'
# app.register_blueprint(b)

@app.route("/")
def index():
    return render_template('betterone.html')

@app.route("/initate", methods=['GET'])
def initate():
    global last_state
    init_state = rdp.init_state()
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    vmd_file = '/home/fan/generate-motion-from-roadmap/server/static/vmd/{0}.vmd'.format(timenow)
    last_state = rdp.motion_generation(init_state, vmd_file, bone_csv_file, False, False)[-1]
    return timenow

@app.route("/gene_motion", methods=['GET'])
def gene_motion():
    global last_state
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    vmd_file = '/home/fan/generate-motion-from-roadmap/server/static/vmd/{0}.vmd'.format(timenow)
    last_state = rdp.motion_generation(last_state, vmd_file, bone_csv_file, False, False)
    return timenow

@app.route('/openface', methods=['POST'])
def openface():
    global fname, fv, fc
    result = {}
    Imgfile = request.files['file']

    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    Imgfile.save('/home/fan/generate-motion-from-roadmap/static/input/{0}.png'.format(timenow))

    os.popen('~/OpenFace/build/bin/FaceLandmarkImg -f /home/fan/generate-motion-from-roadmap/static/input/{0}.png\
              -out_dir /home/fan/generate-motion-from-roadmap/static/output/{1}'.format(timenow, timenow)).readlines()
    try:
        df = pd.read_csv('/home/fan/generate-motion-from-roadmap/static/output/{0}/{1}.csv'.format(timenow, timenow), sep=',')
    except:
        return 'error'

    value = df[[' gaze_0_x', ' gaze_0_y', ' gaze_0_z', ' gaze_1_x', ' gaze_1_y', ' gaze_1_z']].values
    result['left_eye'] = str(value[:][:3])
    result['right_eye'] = str(value[:][3:])
    result['timenow'] = timenow
    looking = gaze_determinator(result)

    if fname != request.form['fname']:
        if fname != None:
            tmp_key = init_states_stack.pop(0)
            tmp_value = routes_stack.pop(0)
            tmp_connects = [x[:40] for x in rdp.routes_dic[tmp_key]]
            if tmp_key in tmp_connects:
                k = tmp_connects.index(tmp_key)
                rdp.routes_dic[tmp_key][k][40] += fv
                rdp.routes_dic[tmp_key][k][41] += fn
            else:
                rdp.routes_dic[tmp_key].append(tmp_value + [fv, fn])
        fname = request.form['fname']
        fc = 1
        fv = looking
    else:
        fc += 1
        fv += looking

    return json.dumps(result)

if __name__ == "__main__":
    # app = make_app()
    # app.jinja_env.auto_reload = True
    # app.run(host='0.0.0.0', debug=True, port=5000, ssl_context='adhoc')
    app.run(port=8008, debug=True)
