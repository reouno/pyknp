import os
import re
import socket
import subprocess
import sys

import six


class Socket(object):

    def __init__(self, hostname, port, option=None):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((hostname, port))
        except:
            raise
        if option is not None:
            self.sock.send(option)
        data = ""
        while "OK" not in data:
            data = self.sock.recv(1024)

    def __del__(self):
        if self.sock:
            self.sock.close()

    def query(self, sentence, pattern):
        assert (isinstance(sentence, six.text_type))
        sentence = sentence.strip() + '\n'  # ensure sentence ends with '\n'
        self.sock.sendall(sentence.encode('utf-8'))
        data = self.sock.recv(1024)
        recv = data
        while not re.search(pattern, recv):
            data = self.sock.recv(1024)
            recv = "%s%s" % (recv, data)
        return recv.strip().decode('utf-8')


class Subprocess(object):

    def __init__(self, command, timeout=180):
        subproc_args = {'stdin': subprocess.PIPE, 'stdout': subprocess.PIPE,
                        'cwd': '.', 'close_fds': sys.platform != "win32"}
        try:
            env = os.environ.copy()
            self.process = subprocess.Popen(command, env=env, **subproc_args)
            self.process_command = command
            self.process_timeout = timeout
        except OSError:
            raise

    def __del__(self):
        self.process.stdin.close()
        self.process.stdout.close()
        try:
            self.process.kill()
            self.process.wait()
        except OSError:
            pass
        except TypeError:
            pass
        except AttributeError:
            pass

    # @timeout_decorator.timeout(5, use_signals=False)
    def query(self, sentence, pattern):
        assert isinstance(sentence, six.text_type)
        # env = os.environ.copy()
        # proc = subprocess.run(self.command, input=(sentence + '\n').encode(), env=env, check=True, **self.subproc_args)
        self.process.stdin.write(sentence.encode())
        self.process.stdin.write('\n'.encode())
        self.process.stdin.flush()
        # print(self.p.stdout.readline().decode().strip())
        result = ''
        # for line in self.p.stdout.readlines():
        while True:
            line = self.process.stdout.readline().decode().strip()
            if re.search(pattern, line):
                break
            result += line + '\n'
        return result
