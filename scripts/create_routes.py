import json

with open('/home/fan/generate-motion-from-roadmap/roadmap/states.txt', 'r') as f:
    states = f.read()
    states = eval(states)
routes_dic = {}
for i in range(len(states)):
    routes_dic[i] = []
print('create routes_dic: done, {0} states in roadmap'.format(len(routes_dic)))
routes_dic = json.dumps(routes_dic)
with open('/home/fan/generate-motion-from-roadmap/roadmap/saved/routes.json', 'w') as f:
    f.write(routes_dic)
