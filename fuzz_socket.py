__author__ = 'HK-BK'
import socket
import random
import time
import string
import os
import sys

hello = "0300001611e00000001200c1020100c2020102c0010a"
set_comm = "0300001902f08032010000000000080000f0000001000101e0"
message = "0300002102f080320700000100000800080001120411440100ff09000400110000"
message_str = "0300002102f080320700000100000800080001120411440100ff09000400110000"
userdata_dict = {0:'01', 1:'02', 2:'03', 3:'07'}
subfunction_dict = {0:'01', 1:'02', 2:'0c', 3:'0e', 4:'0f', 5:'10', 6:'13'}

host = sys.argv[1]
dport = sys.argv[2]

def randomString(n):
    return (''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(n))))[0:16]

def s7head():
    tpkt = message_str[:8]
    cotp = message_str[8:14]
    replay_header_part1 = message_str[14:26]
    replay_headpara = randomString(2).zfill(4)
    replay_headdata = randomString(2).zfill(4)
    replay_header = tpkt + cotp + replay_header_part1 + replay_headpara + replay_headdata
    return replay_header

def s7para():
    parameter_head = message_str[34:40]
    parameter_len = message_str[40:45]
    function_group = str(random.randint(1,7))
    subfunction = subfunction_dict[random.randint(0,6)]
    sequence_number = message_str[48:50]
    replay_parameter = parameter_head + parameter_len + function_group + subfunction + sequence_number
    return replay_parameter

def s7data():
    return_code = message_str[50:52]
    transport_size = message_str[52:54]
    data_len = randomString(2).zfill(4)
    data = randomString(4).zfill(8)
    replaydata = return_code + transport_size + data_len + data
    return replaydata

def str2byte(data):
    base = '0123456789ABCDEF'
    i = 0
    data = data.upper()
    result = ''
    while i < len(data):
        beg = data[i]
        end = data[i+1]
        i += 2
        b1 = base.find(beg)
        b2 = base.find(end)
        if b1 == -1 or b2 == -1:
            return None
        result += chr((b1 << 4) + b2)
    return result

def localtime():
    real_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return real_time

logfile = open('./fuzzlog.log', 'w+')
# os.system('ping 172.18.15.108')
while True:
    replay_pkt = s7head() + s7para() + s7data()
    fuzz_pkt = str2byte(replay_pkt)
    hello_pkt = str2byte(hello)
    comm_pkt = str2byte(set_comm)
    cliconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliconn.connect((host, int(dport)))
    cliconn.send(hello_pkt)
    time.sleep(1)
    cliconn.send(comm_pkt)
    time.sleep(1)
    cliconn.send(fuzz_pkt)
    os.system('ping %s -n 1 -w 3' %host)
    if cliconn.recv == '':
        logfile.write("%s\n%s\n\n" %(localtime(), replay_pkt))
