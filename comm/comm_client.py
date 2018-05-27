
import socket, ssl
from DNA_APP.constants import constant
import cPickle as Pickle
import threading

class Comm_client(threading.Thread):

    def __init__(self,server_address, tree_root, seed, tbit, sec_param):

        threading.Thread.__init__(self)
        self.server_address = server_address
        self.tree_root = tree_root
        self.seed = seed
        self.tbit = tbit
        self.sec_param = sec_param

        self.port = constant.PORT

        self.run()



    def run(self):


        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Require a certificate from the server. We used a self-signed certificate
        # so here ca_certs must be the server certificate itself.
        ssl_sock = ssl.wrap_socket(s,cert_reqs=ssl.CERT_REQUIRED, ca_certs='/Users/admin1/Documents/keys/cert.pem')

        ssl_sock.connect(('127.0.0.1', self.port))

        pickled_data = Pickle.dumps([self.tree_root,self.seed,self.tbit,self.sec_param])

        print "size of pickled data is: %d" %(len(pickled_data))

        ssl_sock.sendall(pickled_data)

        results = self.get_data(ssl_sock)

        #print results

        ssl_sock.close()


    def get_data(self, s):
        data = b''
        while True:
            chunk = s.recv(50)
            if chunk == b'':
                break
            data += chunk

        print('Connection closed')
        s.close()
        return data


