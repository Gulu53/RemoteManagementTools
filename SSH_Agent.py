#!/usr/bin/python 
import sys, pexpect, traceback
import pdb

class SSH_Agent:
    
    def __init__(self, host, user, password):
        self.user = user
        self.host = host
        self.password = password
        self.session = None
    
    def login(self):
        
        ssh_newkey_response = "Are you sure you want to continue connecting"        
        ssh_permission_deny = "Permission denied, please try again."
        ssh_unknown_host = "Name or service not know"
        
        try:
            self.session = pexpect.spawn('ssh {0}@{1}'.format(self.user, self.host))
            ret = self.session.expect([ssh_newkey_response, ssh_unknown_host, "{0}@{1}'s password:".format(self.user, self.host)], timeout=300)
            if ret == 1:
                raise Exception("[-]Destination cannot be resolved.")
            elif ret == 0:
                self.session.sendline('yes')
                self.session.expect("{0}@{1}'s password:".format(self.user, self.host), timeout=300)

            self.session.sendline(self.password)
            if self.session.expect([ssh_permission_deny, '[\$$]'], timeout=60):
                return True
            else:
                raise Exception("[-]Authentication failed.")    
        except pexpect.EOF as e:
            raise pexpect.EOF("[-]EOF exception caught with return message: \n\t" + self.session.before)
        except pexpect.TIMEOUT as e:
            raise pexpect.TIMEOUT("[-]TIMEOUT exception caught.")
        except Exception as e:
            raise Exception("[-]Unexpected error: " + e.args[0])

    def run(self, command, pattern, expect_ret=True, timeout=60):
        if self.session:
            try:
                command_index = None
                self.session.sendline(command)
                if expect_ret:
                    self.session.expect(pattern, timeout=timeout)
                    ret = self.session.before.split('\r\n')
                    for this_ret in ret:
                        if command in this_ret:
                            command_index = ret.index(this_ret)
                            break
                    return ret[command_index+1 : len(ret)-3] 
            except pexpect.EOF as e:
                raise pexpect.EOF("[-]EOF exception caught with return message: \n\t" + self.session.before)
            except pexpect.TIMEOUT as e:
                raise pexpect.TIMEOUT("[-]TIMEOUT exception caught.")
            except Exception as e:
                raise Exception("[-]Unexpected error: " + e.args[0])

            
    def logout(self):
        if self.session:    
            if not self.run('exit', "Connection to {0} closed.".format(self.host)):
                print self.session.before + self.session.after
        else:
            print("No ssh session currently exist.")

    def scp(self, command):

        scp_responses = [ "Are you sure you want to continue connecting",
                          "Permission denied, please try again.", 
                          "Name or service not know",
                          "{0}@{1}'s password:".format(self.user, self.host),
                          pexpect.EOF]
        try:
            scp_session = pexpect.spawn(command)
            ret = scp_session.expect(scp_responses, timeout = 300)
            if ret == 0:
                scp_session.sendline('yes')
                scp_session.expect(scp_responses, timeout = 300)
            elif ret == 2:
                raise Exception("[-]Destination cannot be resolved.") 
            elif ret == 4:
                return True

            scp_session.sendline(self.password)
            
            if scp_session.expect(scp_responses, timeout = 60) == 4:
                return True
            else:
                raise Exception("[-]Authentication failed.")
        except pexpect.EOF as e:
            raise pexpect.EOF("[-]EOF exception caught with return message: \n\t" + scp_session.before)
        except pexpect.TIMEOUT as e:
            raise pexpect.TIMEOUT("[-]TIMEOUT exception caught.")
        except Exception as e:
            raise Exception("[-]Unexpected error: " + e.args[0])
            
def main():
    host = '172.16.11.178'
    user = 'admin'
    password = 'admin'
    ssh_session = SSH_Agent(host, user, password=password)
#    pdb.set_trace()
#    ssh_session.login()
#    pdb.set_trace()
#        ret1 = ssh_session.run('ps -W | grep collector', '[\$$]')
#        print ret1
#    ssh_session.scp('scp admin@172.16.11.178:/cygdrive/c/CFDisk/config/reftags.csv .')

if __name__ == '__main__':
    main()
