"""
Server module
Description: The server module should be deployed on the database server. The module is used to process the received
queries and return the evaluation of the FSS share.
Author: Lavi. Lazarovitz
Date: 10/1/18
"""

from bitstring import BitArray
from prg import prg

def eval(b,K,x,sec_param, check_num):

    """The function evaluates the received function (K) on a given value x

    Args:
        b (bitstring): Either '0' or '1' representing the database number. This bit is also used as the root's T flag
                       bit.
        K (dictionary): K is a dictionary with the following structure - {seed:(bitstring),'0':(bitstring),...}
                        The seed is the root of the tree and each following numbered key ('0','1','2'...) are the different correction
                        words for each tree level.
        x (bitstring): Bitstring of length n (tree depth). x is the value to be evaluated.
        sec_param (int): The number of bits used in each node

    Returns:
        bitstring: The return value is the evaluated bitstring based on the key K and the value x.
    """

    # Setting the seed, T flag and security parameter
    seed = K['seed']
    T_bit = BitArray(bin=b)
    cur_item = None

    tree_depth = len(x)

    # print '----------------eval--------------------'

    # Evaluating the node on the tree path determined by the value x
    for i in xrange(tree_depth):
        # Using the PRG to evaluate the next level of the tree
        Sl_Tl_Sr_Tr = "{0:b}".format(prg(seed)).zfill(2 * sec_param + 2)
        S_T = {'0': {}, '1': {}}

        # Pasring the generated bits
        S_T['0']['S'] = BitArray(bin=Sl_Tl_Sr_Tr[:sec_param])
        S_T['0']['T'] = BitArray(bin=Sl_Tl_Sr_Tr[sec_param])
        S_T['1']['S'] = BitArray(bin=Sl_Tl_Sr_Tr[sec_param + 1: 2 * sec_param + 1])
        S_T['1']['T'] = BitArray(bin=Sl_Tl_Sr_Tr[2 * sec_param + 1])

        S = {}
        T = {}

        CW = BitArray(bin=K[i]['CW'])
        Tbit0 = BitArray(bin=K[i]['0'])
        Tbit1 = BitArray(bin=K[i]['1'])

        # Correcting the seed and T flag bit based on the correction words in the key
        S['0'] = S_T['0']['S'] ^ BitArray(bin=((CW * abs(T_bit.int)).bin).zfill(sec_param))
        S['1'] = S_T['1']['S'] ^ BitArray(bin=((CW * abs(T_bit.int)).bin).zfill(sec_param))
        T['0'] = S_T['0']['T'] ^ BitArray(bin=((Tbit0 * abs(T_bit.int)).bin).zfill(1))
        T['1'] = S_T['1']['T'] ^ BitArray(bin=((Tbit1 * abs(T_bit.int)).bin).zfill(1))

        # Updating the values for the next evaluation
        cur_item = S[x[i]].bin
        seed = S[x[i]].int
        T_bit = T[x[i]]

        if i == (len(x) - 1):

            final_cw = BitArray(bin=K['final_cw'])
            check_bits = BitArray(int=check_num,length=sec_param)
            cur_item = S[x[i]] ^ BitArray(bin=(((final_cw ^ check_bits) * abs(T_bit.int)).bin).zfill(sec_param))


        # print "%d   S%s: %d , S_%s: %s ,  t%s: %s,  cw: %s" %(i,b,seed,b,cur_item,b, T_bit, K[i]['CW'])

    # Returning the bitstring of the last evaluated node
    return cur_item