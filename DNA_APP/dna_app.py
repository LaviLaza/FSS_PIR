
# display identified positive illnesses

#TODO: add threading for client comm
#TODO: conside radding variable type assertion tp validate object type
#TODO: add cert file input
#TODO: add address instead of localhost

from constants import constant
import argparse
import logging
from client import DNA_App_Client, InvalidDNAException
from comm.comm_client import Comm_client
import sys
from bitstring import BitArray



def main():
    # logging.basicConfig(format='%(asctime)s %(filename)s %(funcName)s %(levelname)s %(message)s',
    #                     datefmt='%m/%d/%Y %I:%M:%S %p',filename=r'logs/app.log',level=logging.INFO, filemode='w')

    logging.basicConfig(format='%(asctime)s %(filename)s %(funcName)s %(levelname)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)
    logging.info('App started.')
    parser = argparse.ArgumentParser(description='DNA secret sharing app client')
    parser.add_argument('-f',help='the full paht of the DNA file', required=True, dest='file_name')
    parser.add_argument('-s', help='server 2 IP  - #.#.#.#',required=True, dest='server_ips',nargs=2)
    args = vars(parser.parse_args())

    dna = load_file(args['file_name'])
    try:
        Client = DNA_App_Client(dna)
        secret_share_tree, seed0, seed1 = Client.build_secret_share_trees()

    except InvalidDNAException:
        logging.error("The input DNA string is invalid, please check DNA string in file")

    # send server 1 list of tree object, seed, t bit and sec param - thread
    # send server 2 list of tree object, seed, t bit and sec param - thread

    # listen to response - should be serialized list of results - both threads
    # add corresponding items in each thread

    # try:
    comm_client_1 = Comm_client(args['server_ips'][0], tree_root=secret_share_tree, seed=seed0,
                                    tbit='0', sec_param=constant.SEC_PARAM)
    comm_client_2 = Comm_client(args['server_ips'][1], tree_root=secret_share_tree, seed=seed1,
                                   tbit='1', sec_param=constant.SEC_PARAM)
    comm_client_1.start()
    comm_client_2.start()

    comm_client_1.join()
    comm_client_2.join()

    server1_analysis = comm_client_1.analysis
    server2_analysis = comm_client_2.analysis

    for key, index in zip(server1_analysis,range(1,len(server1_analysis))):
        analysis1 = BitArray(bin=server1_analysis[key])
        analysis2 = BitArray(bin=server2_analysis[key])

        print "The risk of being ill of illness # %d is: %d percent. " %(index,(analysis1 ^ analysis2).int)

    # except Exception as e:
    #     logging.error("Something went wrong while communicating with servers")
    #     print sys.exc_info()[0]


    logging.info('App done.')

def load_file(file_name):

    logging.info('Loading file')
    try:
        with open(file_name, 'r') as dna_file:
            dna = dna_file.readlines()[0]

    except OSError as e:
        print "The file name does not exist."
        logging.error('File does not exist')

    return dna


















if __name__ == "__main__":
    main()



