import socket
from socket import AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET, SHUT_RDWR
import ssl
import cPickle as Pickle
from DNA_APP.constants import constant
from DTs.Dtree_server import Eval
import json
from struct import unpack, pack
from bitstring import BitArray

KEYFILE = constant.SERVER_KEY_FILE_PATH
CERTFILE = constant.SERVER_CERT_FILE_PATH


def convert_dna_to_bitstring(check):
    dna_bitstring = check.replace('A', constant.DNA_DICT['A'])
    dna_bitstring = dna_bitstring.replace('C', constant.DNA_DICT['C'])
    dna_bitstring = dna_bitstring.replace('G', constant.DNA_DICT['G'])
    dna_bitstring = dna_bitstring.replace('T', constant.DNA_DICT['T'])

    return dna_bitstring


def get_data(s):

    try:
        data_size = s.recv(8)
        (length,) = unpack('>Q', data_size)
        data = b''
        while len(data) < length:
            to_read = length - len(data)
            data += s.recv(4096 if to_read > 4096 else to_read)
    except Exception as e:
        print e.message()


    #print('Connection closed')
    #s.close()
    return data

def dna_server(address):
    s = socket.socket(AF_INET, SOCK_STREAM)
    s.bind(address)
    s.listen(1)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    s_ssl = ssl.wrap_socket(s, keyfile=KEYFILE, certfile=CERTFILE, server_side=True)

    #try:
    while 1:
        (c,a) = s_ssl.accept()
        print('Got connection', c, a)
        data = get_data(c)
        #print data
        unpickled_data = Pickle.loads(data)
        print unpickled_data
        results = dna_analysis_single_result(unpickled_data)
        print results
        send_response(c,results)
        #except socket.error as e:
         #   print('Error: {0}'.format(e))
        c.close()

def dna_analysis_single_result(data_list):



    with open(constant.CHECKS_FILE_PATH,'rb') as check_file:
        checks = check_file.readline()
        checks_dict = json.loads(checks)
    max_check = max([int(i) for i in checks_dict.keys()])
    analysis_sum = BitArray(int=0, length=data_list[3] * max_check)

    for check_num, check_dna in checks_dict.items():
        check_bits = convert_dna_to_bitstring(check_dna)
        analysis = Eval(x=check_bits, tree_root=data_list[0], seed=data_list[1], T=data_list[2],
                        sec_param=data_list[3])
        print int(check_num)
        analysis_sum ^= BitArray(int=(BitArray(bin=analysis).int * int(check_num)),length=data_list[3]  * max_check)

    return analysis_sum.bin

def dna_analysis_percentage(data_list):

    analysis_result = {}


    with open(constant.CHECKS_FILE_PATH,'rb') as check_file:
        checks = check_file.readline()
        checks_dict = json.loads(checks)

    for check_num, check_dna in checks_dict.items():
        check_bits = convert_dna_to_bitstring(check_dna)
        analysis = Eval(x=check_bits, tree_root=data_list[0], seed=data_list[1], T=data_list[2],
                        sec_param=data_list[3])
        analysis_result[check_num] = analysis
    return analysis_result

def send_response(client_sock, results):

    pickled_response = Pickle.dumps(results)
    print len(pickled_response)

    length = pack('>Q', len(pickled_response))
    client_sock.sendall(length)
    client_sock.sendall(pickled_response)

dna_server(('', 8082))

