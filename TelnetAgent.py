#!/usr/bin/python3

import telnetlib

class TelnetAgent(object):

    def __init__(self, host_name, user, password, prompt, timeout = 2):
        self.host_name = host_name
        self.user = user
        self.password = password
        self.prompt = prompt
        self.timeout = timeout
        self.tn = None

    def login(self):
        try:
            self.tn = telnetlib.Telnet(self.host_name)
            try:    
                self.tn.read_until(b'login: ')
                self.tn.write(self.user.encode() + b'\r\n')
                self.tn.read_until(b'Password: ')
                self.tn.write(self.password.encode() + b'\r\n')
                if self.prompt in self.tn.read_until(self.prompt.encode(), self.timeout).decode():
                    return True
                else:
                    raise EOFError("[-]Authentication Failed.")
            except Exception as e:
                raise e
        except Exception as e:
            raise e 

    def logout(self):
    	self.tn.close()    

    def run(self, command):
        try:
            self.tn.write(command.encode() + b'\r\n')
            return ((self.tn.read_until('>$'.encode(), self.timeout).decode()).splitlines())[:-1]
        except EOFError as e:
            raise EOFError("[-]Connection closed unexpectedly.")
        except Exception as e:
            raise Exception("[-]Unexpected error: " + e.args[0])

    def get_pid(self, pid_table, process_list = None):
    
        pid_dictionary = dict()

        for process in pid_table:
	        if process_list:
		        for target_process in process_list:
			        if target_process in process.lower():
				        pid_dictionary[process[process.index("File=") + 5 : len(process)]] = process[process.index("PID=0x") + 4 : process.index("Threads")].rstrip()
	        else:
		        pid_dictionary[process[process.index("File=") + 5 : len(process)]] = process[process.index("PID=0x") + 4 : process.index("Threads")].rstrip()

        return pid_dictionary

def main():
    telnetcon =  TelnetAgent('172.16.11.163', 'admin', 'admin', '\> ')
    process_list = ['collectorce','datasender','retriever','ntpclient']

    try:
        if telnetcon.login():
            #telnetcon.run('reboot')
            import pdb; pdb.set_trace()
            telnetcon.run('cd \CFDisk\output')
            ret = telnetcon.run('dir')
            telnetcon.run('del output.csv.temp')
            telnetcon.logout()
    except telnetlib.EOFError as e:
        pass

if __name__ == '__main__':
    main()



