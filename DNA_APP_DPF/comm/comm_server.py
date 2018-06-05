import socket
from socket import AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET, SHUT_RDWR
import ssl
import cPickle as Pickle
from DNA_APP_DPF.constants import constant
from server import eval
import json
from struct import unpack, pack
from bitstring import BitArray
from itertools import chain, combinations, product
import logging

KEYFILE = constant.SERVER_KEY_FILE_PATH
CERTFILE = constant.SERVER_CERT_FILE_PATH


def convert_dna_to_bitstring(check):
    dna_bitstring = check.replace('A', constant.DNA_DICT['A'])
    dna_bitstring = dna_bitstring.replace('C', constant.DNA_DICT['C'])
    dna_bitstring = dna_bitstring.replace('G', constant.DNA_DICT['G'])
    dna_bitstring = dna_bitstring.replace('T', constant.DNA_DICT['T'])

    return dna_bitstring


def get_data(s):

    logging.info("Getting data from client")

    try:
        data_size = s.recv(8)
        (length,) = unpack('>Q', data_size)
        data = b''
        while len(data) < length:
            to_read = length - len(data)
            data += s.recv(4096 if to_read > 4096 else to_read)
    except Exception as e:
        logging.error("Something went wrong when retrieving data %s" %(e.message))


    #print('Connection closed')
    #s.close()
    return data

def dna_server(address):
    logging.info("DNA server started")
    s = socket.socket(AF_INET, SOCK_STREAM)
    s.bind(address)
    s.listen(1)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    s_ssl = ssl.wrap_socket(s, keyfile=KEYFILE, certfile=CERTFILE, server_side=True)

    #try:
    while 1:
        try:
            (c,a) = s_ssl.accept()
            logging.info('Got connection %s %s' %(c, a))
            data = get_data(c)
            #print data
            unpickled_data = Pickle.loads(data)
            logging.info(unpickled_data)
            results = dna_analysis_dpf_single_check(unpickled_data)
            # print results
            send_response(c,results)
            #except socket.error as e:
             #   print('Error: {0}'.format(e))
        finally:
            c.close()

def dna_analysis_dpf_single_check(data_list):

    logging.info("Analyzing DNA")

    with open(constant.CHECKS_FILE_PATH,'rb') as check_file:
        checks_dict = json.load(check_file)

    analysis_sum = BitArray(int=0, length=data_list[3])

    logging.info("Server analysis started")

    for check_num, check_dna in checks_dict.items():
        checks = hamming_ball(check_dna,data_list[2],constant.valid_dna)
        switch = 0
        for check in checks:
            # print check
            check_bits = convert_dna_to_bitstring(check)
            if switch == 0:
                logging.info("eval started")
            analysis = eval(b=data_list[1],K=data_list[0],x=check_bits,sec_param=data_list[3], check_num=int(check_num))
            if switch == 0:
                logging.info("eval done")
                switch += 1
            analysis_sum ^= analysis

    logging.info("Server analysis done")
    return analysis_sum.bin

def send_response(client_sock, results):

    logging.info("Sending analysis to client")

    pickled_response = Pickle.dumps(results)
    # print len(pickled_response)

    length = pack('>Q', len(pickled_response))
    client_sock.sendall(length)
    client_sock.sendall(pickled_response)


def hamming_circle(s, n, alphabet):
    """Generate strings over alphabet whose Hamming distance from s is
    exactly n.

    >>> sorted(hamming_circle('abc', 0, 'abc'))
    ['abc']
    >>> sorted(hamming_circle('abc', 1, 'abc'))
    ['aac', 'aba', 'abb', 'acc', 'bbc', 'cbc']
    >>> sorted(hamming_circle('aaa', 2, 'ab'))
    ['abb', 'bab', 'bba']

    """
    for positions in combinations(range(len(s)), n):
        for replacements in product(range(len(alphabet) - 1), repeat=n):
            cousin = list(s)
            for p, r in zip(positions, replacements):
                if cousin[p] == alphabet[r]:
                    cousin[p] = alphabet[-1]
                else:
                    cousin[p] = alphabet[r]
            yield ''.join(cousin)

def hamming_ball(s, n, alphabet):
    """Generate strings over alphabet whose Hamming distance from s is
    less than or equal to n.

    >>> sorted(hamming_ball('abc', 0, 'abc'))
    ['abc']
    >>> sorted(hamming_ball('abc', 1, 'abc'))
    ['aac', 'aba', 'abb', 'abc', 'acc', 'bbc', 'cbc']
    >>> sorted(hamming_ball('aaa', 2, 'ab'))
    ['aaa', 'aab', 'aba', 'abb', 'baa', 'bab', 'bba']

    """

    logging.info("Calculating string with Hamming distance s")

    return chain.from_iterable(hamming_circle(s, i, alphabet)
                               for i in range(n + 1))




if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(filename)s %(funcName)s %(levelname)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    dna_server(('', 8082))

