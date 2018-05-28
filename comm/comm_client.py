
import socket, ssl
from DNA_APP.constants import constant
import cPickle as Pickle
import threading
from struct import pack, unpack

class Comm_client(threading.Thread):

    def __init__(self,server_address, tree_root, seed, tbit, sec_param):

        threading.Thread.__init__(self)
        self.server_address = server_address
        self.tree_root = tree_root
        self.seed = seed
        self.tbit = tbit
        self.sec_param = sec_param
        self.analysis = None

        self.port = constant.PORT



    def run(self):


        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Require a certificate from the server. We used a self-signed certificate
        # so here ca_certs must be the server certificate itself.
        ssl_sock = ssl.wrap_socket(s,cert_reqs=ssl.CERT_REQUIRED, ca_certs=constant.SERVER_CERT_FILE_PATH)

        ssl_sock.connect((self.server_address, self.port))

        pickled_data = Pickle.dumps([self.tree_root,self.seed,self.tbit,self.sec_param])

        print "size of pickled data is: %d" %(len(pickled_data))

        length = pack('>Q', len(pickled_data))
        ssl_sock.sendall(length)
        ssl_sock.sendall(pickled_data)

        results = self.get_data(ssl_sock)
        results = Pickle.loads(results)

        print results
        self.analysis = results

        ssl_sock.close()


    def get_data(self, s):

        data_size = s.recv(8)
        (length,) = unpack('>Q', data_size)
        data = b''
        while len(data) < length:
            to_read = length - len(data)
            data += s.recv(4096 if to_read > 4096 else to_read)


        print('Connection closed')
        s.close()
        return data


