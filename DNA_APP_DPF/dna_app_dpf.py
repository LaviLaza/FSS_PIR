
# display identified positive illnesses

#TODO: add threading for client comm
#TODO: conside radding variable type assertion tp validate object type
#TODO: add cert file input
#TODO: add address instead of localhost

from constants import constant
import argparse
import logging
from bitstring import BitArray
from errors import InvalidDNAException
from client import DNA_App_Client
from DNA_APP_DPF.comm.comm_client import Comm_client



def main():
    # logging.basicConfig(format='%(asctime)s %(filename)s %(funcName)s %(levelname)s %(message)s',
    #                     datefmt='%m/%d/%Y %I:%M:%S %p',filename=r'logs/app.log',level=logging.INFO, filemode='w')

    logging.basicConfig(format='%(asctime)s %(filename)s %(funcName)s %(levelname)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)
    logging.info('App started.')
    parser = argparse.ArgumentParser(description='DNA secret sharing app client')
    parser.add_argument('-f',help='the full path of the DNA file', required=True, dest='file_name')
    parser.add_argument('-s', help='server 2 IP  - #.#.#.#',required=True, dest='server_ips',nargs=2)
    parser.add_argument('-d', help='max distance off of the client DNA', dest='dist',required=True, type=int)
    args = vars(parser.parse_args())
    # print (args['dist'])
    dna = load_file(args['file_name'])
    try:
        Client = DNA_App_Client(dna)
        logging.info("Starting building CW structure ")
        k0,k1,randomness = Client.build_function()
        logging.info("Done building CW structure")

    except InvalidDNAException as e:
        logging.error("The input DNA string is invalid, please check DNA string in file")

    logging.info("Sending data over to the servers")
    # try:
    comm_client_1 = Comm_client(k=k0,tbit='0', server_address=args['server_ips'][0], distance=args['dist'])
    comm_client_2 = Comm_client(k=k1,tbit='1',server_address=args['server_ips'][1], distance=args['dist'])
    comm_client_1.start()

    # comm_client_1.run()
    # comm_client_2.run()
    comm_client_2.start()

    comm_client_1.join()
    comm_client_2.join()

    logging.info("Retrieving analysis from servers.")
    server1_analysis = comm_client_1.analysis
    server2_analysis = comm_client_2.analysis

    logging.info("Analyzing results")
    if (BitArray(bin=server1_analysis) ^ BitArray(bin=server2_analysis)).int == 0:
        print "No disease found"
    else:
        analysis = (BitArray(bin=server1_analysis) ^ BitArray(bin=server2_analysis) ^ BitArray(bin=randomness)).int
        print 'The client DNA matches disease # : %d' %(analysis)

    logging.info('App done.')

def load_file(file_name):

    logging.info('Loading file')
    try:
        with open(file_name, 'r') as dna_file:
            dna = dna_file.readline()

    except OSError as e:
        print "The file name does not exist."
        logging.error('File does not exist')

    return dna


















if __name__ == "__main__":
    main()



