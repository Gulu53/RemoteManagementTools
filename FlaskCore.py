#!/usr/bin/python
from flask import Flask
import subprocess

app =  Flask(__name__)

@app.route('/Restart')
def restart_all():
    init();
    subprocess.call('../RemoteManagementTools/Rrestart.py', shell=True)
    return check();

@app.route('/Restart/<reader>')
def restart_reader(reader):
    init();
    subprocess.call('../RemoteManagementTools/Rrestart.py -r {0}'.format(reader), shell=True)
    return check();

@app.route('/Restart/<reader>/<process>')
def restart_reader_proc(reader, process):
    init();
    subprocess.call('../RemoteManagementTools/Rrestart.py -r {0} --ap {1}'.format(reader, process), shell=True)
    return check();

@app.route('/Reboot/<reader>')
def reboot_reader(reader):
    init();
    subprocess.call('../RemoteManagementTools/Rrestart.py -r {0} --reboot True'.format(reader), shell=True)
    return check();

@app.route('/Reboot')
def reboot_all():
    init();
    subprocess.call('../RemoteManagementTools/Rrestart.py --reboot True'.format(reader), shell=True)
    return check();

def check():
    ret = int(subprocess.check_output('cat ../RemoteManagementTools/Rrestart.log | grep -i error | wc -l', shell=True).rstrip('\n'))  
    if (ret):
        return ('ERROR '+ subprocess.check_output('cat ../RemoteManagementTools/Rrestart.log | grep -i error', shell=True))
    else:
        return ('SUCCESS ' + subprocess.check_output('cat ../RemoteManagementTools/Rrestart.log', shell=True))

def init():
    subprocess.call('bash ../clearRemoteLog.sh', shell=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
