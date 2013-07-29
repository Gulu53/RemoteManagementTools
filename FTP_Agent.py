#!/usr/bin/python2
import pexpect
import pdb

class FTP_Agent:

    def __init__(self, host, user, password):
        self.user = user
        self.host = host
        self.password = password
        self.session = None
        self.expected_resp = ["(?i)name .*: ",
                              "Password:",
                              "Login failed.",
                              "Name or service not known",
                              "ftp> "]
    def login(self):
        try:
            self.session = pexpect.spawn('ftp {0}'.format(self.host))
            ret = self.session.expect(self.expected_resp, timeout = 60)
            if ret==3 or ret==4 :
                raise Exception("[-]FTP session failed due to " + self.expected_resp[ret])

            self.session.sendline(self.user)
            if self.session.expect(self.expected_resp, timeout = 60) == 1:
                self.session.sendline(self.password.encode())
                if self.session.expect(self.expected_resp, timeout = 60) == self.expected_resp.index("ftp> "):
                    return True
        except pexpect.EOF:
            raise pexpect.EOF("[-]FTP session closed due to " + self.session.before)
        except pexpect.TIMEOUT as e:
            raise pexpect.TIMEOUT("[-]Timeout exception caught.")
        except Exception as e:
            raise Exception("[-]Unexpected error: " + e.args[0])

    def logout(self):
        if self.session:
           self.session.close()

    def run(self, command):
        if self.session:
            self.session.sendline(command)
            if self.session.expect(self.expected_resp, timeout=60) == self.expected_resp.index("ftp> "):
                ret = self.session.before.split("\r\n") 
                return ret[1:len(ret)-1]
        else:
            raise Exception("[-]No existing FTP connections identified.")

def main():
    host = "172.16.11.179"
    user = "admin"
    password = "admin"
    command = ['dir', 'cd /CFDisk', 'prompt', 'mput ./test.txt']

    a = FTP_Agent(host, user, password)
    if a.login():
        for each_command in command:
            for each_ret in a.run(each_command):
                print each_ret

if __name__ == "__main__":
    main()
