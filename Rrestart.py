#!/usr/bin/python

from SSH_Agent import SSH_Agent
from TelnetAgent import TelnetAgent
from threading import Thread
import optparse, pdb, threading
from time import sleep

def moxa_readers_restart(enclosure, applications_list, hard_reboot_flag=False):
    telnetcon = TelnetAgent(enclosure, 'admin', 'admin', '\> ')
    try:
        if telnetcon.login():
            while True:
                if not moxa_readers_apps_kill(telnetcon, applications_list, hard_reboot_flag):
                    break
            if not hard_reboot_flag:
                while True:
                    if moxa_readers_apps_start(telnetcon, applications_list):     
                        break
            else:
                telnetcon.run("reboot")
        print("Reader {0} restarted.".format(enclosure))
    except Exception as e:
        raise e

def moxa_readers_apps_kill(telnetcon, applications_list, hard_reboot_flag):
    ret = telnetcon.get_pid(telnetcon.run('ps'), applications_list)
    buffer_del_flag = False

    for each_process in ret:
        if 'datasender' in each_process.lower():
            buffer_del_flag = True
        telnetcon.run("ps -k " + ret[each_process])
    if buffer_del_flag and hard_reboot_flag:
        telnetcon.run('cd \CFDisk\output')
        telnetcon.run('move output.csv output.csv.temp')
        telnetcon.run('del output.csv.temp')
    return len(telnetcon.get_pid(telnetcon.run('ps'), applications_list))

def moxa_readers_apps_start(telnetcon, applications_list):
    count = 0
    telnetcon.run('cd \CFDisk\config')
    for this_line in telnetcon.run('dir'):
        for this_app in applications_list:
            
            if 'ntpclient' in this_app.lower():
                if 'services.bat' in this_line.lower():
                    telnetcon.run('start Services.bat')
                    count += 1
            else:
                if this_app.lower() in this_line.lower():
                    telnetcon.run('start ' + this_line.split()[-1])
                    count += 1

        if count == len(applications_list):
            break
    return len(applications_list) == len(telnetcon.get_pid(telnetcon.run('ps'), applications_list)) 
    
def uno1150_readers_restart(enclosure, applications_list, hard_reboot_flag=False):    
    SSH_con = SSH_Agent(enclosure, 'admin', 'admin')
    try:
        if SSH_con.login():
            while True:
                if not uno1150_reader_apps_kill(SSH_con, applications_list):
                    break
            if not hard_reboot_flag:
                while True:
                    if uno1150_reader_apps_start(SSH_con, applications_list):
                        break
            else:
                SSH_con.run("restart",'[\$$]', expect_ret=False)
        print("Reader {0} restarted.".format(enclosure))
    except Exception as e:
        raise e

def uno1150_reader_apps_kill(SSH_con, applications_list):
    prompt = '[\$$]'
    pid_list = []
    search_string = ""
    
    search_string += applications_list[0]

    for each_app in applications_list:
        if not each_app in search_string:
            search_string += '\|'
            search_string += each_app
        pid_list.append(SSH_con.run('ps -W | grep {0}'.format(each_app), prompt)[0].split()[0])
    for each_pid in pid_list:
        SSH_con.run('taskkill /F /PID {0}'.format(each_pid), prompt)
    return SSH_con.run("ps -W | grep '{0}'".format(search_string), prompt)

def uno1150_reader_apps_start(SSH_con, applications_list):
    prompt = '[\$$]'
    search_string = applications_list[0]
    
    SSH_con.run('cd /cygdrive/c/CFDisk/config', prompt)
    for each_app in applications_list:
        if not each_app in search_string:
            search_string += '\|'
            search_string += each_app
        bash_script = SSH_con.run('ls | grep .bat | grep -i {0}'.format(each_app), prompt)[0]
        SSH_con.run('./{0}'.format(bash_script), prompt)
    
    return len(applications_list) == len(SSH_con.run("ps -W | grep '{0}'".format(search_string), prompt))
 
def main():
    moxa_readers = ['161', '162', '163', '164', '165', '166', '167', '168', '169', '170', '175', '176']
    uno1150_readers = ['177', '178', '179']
    default_applications = ['ntpclient', 'collector', 'retriever', 'datasender']
    target_reader = []
    target_app = []
    reboot_flag = False
    
    parser =  optparse.OptionParser("usage%prog " +\
            "-r <Target Readers> --ap <Target Applications(Optional)> --reboot <Hard reboot boolean options(False by default)>")
    parser.add_option('-r', dest='input_reader_list', type='string',\
            help='Specify the target readers')
    parser.add_option('--ap', dest='input_application_list', type='string',\
            help='Specify the application list.')
    parser.add_option('--reboot', dest='input_reboot_decision', type='string',\
            help='Reboot decision.')

    (options, args) = parser.parse_args()
    if not options.input_reader_list:
        target_reader = moxa_readers
        target_reader.extend(uno1150_readers)
    else:
        if ',' in options.input_reader_list:
            target_reader.extend(options.input_reader_list.split(',')) 
        else:
            target_reader.append(str(int(options.input_reader_list)))

    if options.input_application_list:
        if ',' in options.input_application_list:
            target_app.extend(options.input_application_list.split(','))
        else:
            target_app.append(options.input_application_list)
    else:
        target_app = default_applications
        
    if options.input_reboot_decision:
        reboot_flag = True

    if reboot_flag:
        print("System reboot is going to execute.")
    else:
        print("Application reboot is going to exceute.")
    
    print("Following readers will be restarted:")
    for each_reader in target_reader:
        print each_reader
    print("Following applications will be shut down:")
    for each_app in target_app:
        print each_app

    for each_reader in target_reader:
        try:
            if each_reader in moxa_readers:
                t = Thread(target=moxa_readers_restart, args=('172.16.11.{0}'.format(each_reader), target_app, reboot_flag))
                t.start()
            elif each_reader in uno1150_readers:
                t = Thread(target=uno1150_readers_restart, args=('172.16.11.{0}'.format(each_reader), target_app, reboot_flag))
                t.start()
        except telnetlib.EOFError as e:
            print e.args[0]
        except pexpect.TIMEOUT as e:
            print e.args[0]
        except pexpect.EOF as e:
            print e.args[0]
        except Exception as e:
            print e.args[0]
    
    for thread in threading.enumerate():
        if thread is not threading.currentThread():
            thread.join()
    


    exit(0)
                    
if __name__ == "__main__":
    main()

