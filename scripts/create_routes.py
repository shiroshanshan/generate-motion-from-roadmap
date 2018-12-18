import json
import os

PATH = os.getcwd()

with open('{0}/roadmap/states.txt'.format(PATH), 'r') as f:
    states = f.read()
    states = eval(states)
routes_dic = {}
for i in range(len(states)):
    routes_dic[i] = []
print('create routes_dic: done, {0} states in roadmap'.format(len(routes_dic)))
routes_dic = json.dumps(routes_dic)
with open('{0}/roadmap/saved/routes.json'.format(PATH), 'w') as f:
    f.write(routes_dic)
