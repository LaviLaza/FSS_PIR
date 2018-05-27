"""
Key generation module
Description: The key generation module generates 2 keys (K_0,K_1). The keys are dictionaries containing a seed and
correction words for each of the FSS tree levels
Author: Lavi. Lazarovitz
Date: 10/1/18

TODO: Check all zero seed.
"""

import random
from bitstring import BitArray
from dt_prg import prg



def gen(sec_param, a):

    """The function generates the 2 keys (K_0,K_1) for the FSS client.

    Args:
        sec_param (int): The security parameter of the keys. The security parameter will be used to determine the
                         the number of bits of each node in the FSS tree.
        a (bitstring): The variable a is a bitstring representing the path from the root of the FSS tree to
                       the element the client is interested in. 0 - means left path; 1 - means right path.

    Returns:
        list: The function returns a list of 2 dictionary items. Each of the items contains a seed (key: 'seed')
              and the correction words (key: #, the key is an integer of the FSS tree lelvel.

    TODO: Allow to choose the bit foe the intervals + allow inclusive intervals
    """

    # Generating random seeds for each of the keys
    cryptogen = random.SystemRandom()

    S_0 = S_1 = 0
    while (S_0 == S_1):
        S_0 = seed_srv_0 = cryptogen.randrange(2 ** sec_param)
        S_1 = seed_srv_1 = cryptogen.randrange(2 ** sec_param)

    # Setting the seeds in each key. K_0 & K_1 are the keys to be returned
    K_0 = {'seed': S_0}
    K_1 = {'seed': S_1}

    T_srv_0 = BitArray(bin='0')
    T_srv_1 = BitArray(bin='1')

    tree_depth = len(a)

    # Creating the correction word for each level of the trees
    for i in xrange(tree_depth):
        # Using the PRG to get pseudo-random strings for the 2 lower level nodes
        Sl_Tl_Sr_Tr_0 = "{0:b}".format(prg(seed_srv_0)).zfill(2 * sec_param + 4)
        Sl_Tl_Sr_Tr_1 = "{0:b}".format(prg(seed_srv_1)).zfill(2 * sec_param + 4)

        # Using Left = 0, Right = 1
        # The S_T dictionary is used to store the different parts of each tree's key
        # S_T['0'],S_T['1'] - are the two trees
        # S_T[]['0'],S_T[]['1'] - are the different nodes (left,right) in each tree
        # S_T['']['']['S'],S_T['']['']['T'] - are either the seed or the t flag for each node
        S_T = {'0': {'0': {}, '1': {}}, '1': {'0': {}, '1': {}}}

        # Parsing the S and T for each node in each tree
        S_T['0']['0']['S'] = BitArray(bin=Sl_Tl_Sr_Tr_0[:sec_param])
        S_T['0']['0']['T'] = BitArray(bin=Sl_Tl_Sr_Tr_0[sec_param])
        S_T['0']['0']['L'] = BitArray(bin=Sl_Tl_Sr_Tr_0[sec_param + 1]) #left contribution bit
        S_T['0']['1']['S'] = BitArray(bin=Sl_Tl_Sr_Tr_0[sec_param + 2: 2 * sec_param + 2])
        S_T['0']['1']['T'] = BitArray(bin=Sl_Tl_Sr_Tr_0[2 * sec_param + 2])
        S_T['0']['1']['R'] = BitArray(bin=Sl_Tl_Sr_Tr_0[2 * sec_param + 3]) #right contribution bit

        S_T['1']['0']['S'] = BitArray(bin=Sl_Tl_Sr_Tr_1[:sec_param])
        S_T['1']['0']['T'] = BitArray(bin=Sl_Tl_Sr_Tr_1[sec_param])
        S_T['1']['0']['L'] = BitArray(bin=Sl_Tl_Sr_Tr_1[sec_param + 1]) #left contribution bit
        S_T['1']['1']['S'] = BitArray(bin=Sl_Tl_Sr_Tr_1[sec_param + 2: 2 * sec_param + 2])
        S_T['1']['1']['T'] = BitArray(bin=Sl_Tl_Sr_Tr_1[2 * sec_param + 2])
        S_T['1']['1']['R'] = BitArray(bin=Sl_Tl_Sr_Tr_1[2 * sec_param + 3]) #right contribution bit

        # Determining what node is on the path (keep - on the path, loose - not on the path)
        Keep_Lose = BitArray(bin=a[i])
        # Calculating the seed part of the correction word
        S_cw = S_T['0'][(~Keep_Lose).bin]['S'] ^ S_T['1'][(~Keep_Lose).bin]['S']

        # Calculating the T flag bit
        T_cw = {}
        T_cw['0'] = S_T['0']['0']['T'] ^ S_T['1']['0']['T'] ^ Keep_Lose ^ BitArray(bin='1')
        T_cw['1'] = S_T['0']['1']['T'] ^ S_T['1']['1']['T'] ^ Keep_Lose

        # Calcualting the correction contribution bit
        contribution_bit = {}
        # Left correction contribution bit is dependent on the decision path
        contribution_bit['0'] = S_T['0']['0']['L'] ^ S_T['1']['0']['L'] ^ Keep_Lose
        # Righ7ct correction contribution bit is always just xor between the contribution
        # bits (when 1 is the interval flag)
        contribution_bit['1'] = S_T['0']['1']['R'] ^ S_T['1']['1']['R']

        # Setting the keys for the current level
        K_0[i] = {'CW': S_cw, '0': T_cw['0'], 'L': contribution_bit['0'] ,'1': T_cw['1'], 'R': contribution_bit['1']}
        K_1[i] = {'CW': S_cw, '0': T_cw['0'], 'L': contribution_bit['0'], '1': T_cw['1'], 'R': contribution_bit['1']}

        # Calculating the seeds based on the calculated correction word
        seed_srv_0 = (S_T['0'][Keep_Lose.bin]['S'] ^
                                                BitArray(bin=((S_cw * abs(T_srv_0.int)).bin).zfill(sec_param)))
        seed_srv_1 = (S_T['1'][Keep_Lose.bin]['S'] ^
                                                BitArray(bin=((S_cw * abs(T_srv_1.int)).bin).zfill(sec_param)))

        # Calculating the T flag bit based on the calculated correction bit
        T_srv_0 = S_T['0'][Keep_Lose.bin]['T'] ^ \
                                                BitArray(bin=((T_cw[Keep_Lose.bin] * abs(T_srv_0.int)).bin).zfill(1))
        T_srv_1 = S_T['1'][Keep_Lose.bin]['T'] ^ \
                                                BitArray(bin=((T_cw[Keep_Lose.bin] * abs(T_srv_1.int)).bin).zfill(1))


        print "%d   S0_int: %s , S0: %s ,  t0: %s,  cw: %s, | S1_int: %s , S1: %s ,  t1: %s,  cw: %s" \
              %(i,seed_srv_0.int,seed_srv_0.bin, T_srv_0, S_cw.bin,seed_srv_1.int ,seed_srv_1.bin, T_srv_1, S_cw.bin)

        seed_srv_1 = seed_srv_1.int
        seed_srv_0 = seed_srv_0.int
    return K_0, K_1

if __name__ == "__main__":
    print gen(5, '1010')