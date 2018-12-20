import os

PATH = os.getcwd()
os.popen('rm -rf {0}/server/static/vmd/*'.format(PATH)).readlines()
os.popen('rm -rf {0}/server/static/input/*'.format(PATH)).readlines()
os.popen('rm -rf {0}/server/static/output/*'.format(PATH)).readlines()
os.popen('rm -rf {0}/logs/*'.format(PATH)).readlines()
os.popen('rm -rf {0}/readed/*'.format(PATH)).readlines()
print('/server/vmd cleared!')
print('/server/static/input/* cleared!')
print('/server/static/output/* cleared!')
print('/logs/* cleared!')
print('/readed/* cleared!')
