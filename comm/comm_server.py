import socket
from socket import AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET, SHUT_RDWR
import ssl
import cPickle as Pickle
from DNA_APP.constants import constant
from DTs.Dtree_server import Eval
import json


KEYFILE = constant.SERVER_KEY_FILE_PATH
CERTFILE = constant.SERVER_CERT_FILE_PATH


def convert_dna_to_bitstring(check):
    dna_bitstring = check.replace('A', constant.DNA_DICT['A'])
    dna_bitstring = dna_bitstring.replace('C', constant.DNA_DICT['C'])
    dna_bitstring = dna_bitstring.replace('G', constant.DNA_DICT['G'])
    dna_bitstring = dna_bitstring.replace('T', constant.DNA_DICT['T'])

    return dna_bitstring


def get_data(s):
    data = b''
    while True:
        chunk = s.recv(8192)
        if chunk == b'':
            break
        data += chunk

    s.send(b'This is a response.')
    print('Connection closed')
    s.close()
    return data

def dna_server(address):
    s = socket.socket(AF_INET, SOCK_STREAM)
    s.bind(address)
    s.listen(1)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    s_ssl = ssl.wrap_socket(s, keyfile=KEYFILE, certfile=CERTFILE, server_side=True)

    while True:
        try:
            (c,a) = s_ssl.accept()
            print('Got connection', c, a)
            data = get_data(c)
            unpickled_data = Pickle.loads(data)
            results = dna_analysis(unpickled_data)
            print results
            send_response(c,results)
        except socket.error as e:
            print('Error: {0}'.format(e))

def dna_analysis(data_list):

    analysis_result = {}

    with open(constant.CHECKS_FILE_PATH,'rb') as check_file:
        checks = check_file.readline()
        checks_dict = json.loads(checks)
    for check_name, check_dna in checks_dict.items():
        check_bits = convert_dna_to_bitstring(check_dna)
        analysis = Eval(x=check_bits, tree_root=data_list[0], seed=data_list[1], T=data_list[2],
                        sec_param=data_list[3])
        analysis_result[check_name] = analysis
    return analysis_result

def send_response(client_sock, results):

    pickled_response = Pickle.dumps(results)
    print len(pickled_response)
    client_sock.sendall(pickled_response)



dna_server(('', 8082))

