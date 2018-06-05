
import socket, ssl
from DNA_APP_DPF.constants import constant
import cPickle as Pickle
import threading
from struct import pack, unpack
import logging

class Comm_client(threading.Thread):

    def __init__(self,k, server_address, tbit, distance):

        threading.Thread.__init__(self)
        self.server_address = server_address
        self.tbit = tbit
        self.key = k
        self.port = constant.PORT
        self.analysis = None
        self.distance = distance



    def run(self):


        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Require a certificate from the server. We used a self-signed certificate
        # so here ca_certs must be the server certificate itself.
        ssl_sock = ssl.wrap_socket(s,cert_reqs=ssl.CERT_REQUIRED, ca_certs=constant.SERVER_CERT_FILE_PATH)

        ssl_sock.connect((self.server_address, self.port))

        pickled_data = Pickle.dumps([self.key, self.tbit, self.distance, constant.SEC_PARAM])

        # print "size of pickled data is: %d" %(len(pickled_data))

        length = pack('>Q', len(pickled_data))
        logging.info("Number of bytes send to server: %d" %(len(pickled_data)))
        ssl_sock.sendall(length)
        ssl_sock.sendall(pickled_data)

        results = self.get_data(ssl_sock)
        results = Pickle.loads(results)

        # print results
        self.analysis = results

        ssl_sock.close()


    def get_data(self, s):

        logging.info("Getting analysis from server")

        data_size = s.recv(8)
        (length,) = unpack('>Q', data_size)
        logging.info("Number of bytes received from server: %s" %(length))
        data = b''
        while len(data) < length:
            to_read = length - len(data)
            data += s.recv(4096 if to_read > 4096 else to_read)


        # print('Connection closed')
        s.close()
        return data


