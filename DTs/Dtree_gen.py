
import random
from bitstring import BitArray
from Dtree_prg import prg
import Queue

def generate_DT(tree_root, sec_param):

    cryptogen = random.SystemRandom()

    S_0 = S_1 = 0
    while (S_0 == S_1):
        S_0 = cryptogen.randrange(2 ** sec_param)
        S_1 = cryptogen.randrange(2 ** sec_param)

    tree_root.seed = root_seeds = [S_0,S_1]
    tree_root.Tbit = [BitArray(bin='0'), BitArray(bin='1')]

    queue = Queue.Queue()
    queue.put(tree_root)
    counter = 0

    while not queue.empty():
        node = queue.get()
        calculate(node, sec_param)
        if not node.left_child.is_leaf:
            queue.put(node.left_child)
        if not node.right_child.is_leaf:
            queue.put(node.right_child)

        node.seed = None
        node.Tbit = None
        node.left_bit = None
        node.right_bit = None
        node.value = None
        node.true_path_flag = None

    tree_root.seed = root_seeds

    return tree_root


def calculate(node, sec_param):
    
    L = {'0' : {}, '1': {}}
    L_T = {'0' : {}, '1': {}}
    R = {'0' : {}, '1': {}}
    R_T = {'0' : {}, '1': {}}

    # zfill is actually a problem. I need to have random string not 0 fills...
    extended_seed_0 = "{0:b}".format(prg(node.seed[0], 4)).zfill(4 * sec_param + 4)
    extended_seed_1 = "{0:b}".format(prg(node.seed[1], 4)).zfill(4 * sec_param + 4)
    
    L['0']['0'] = BitArray(bin=extended_seed_0[:sec_param])
    L_T['0']['0'] = BitArray(bin=extended_seed_0[sec_param])
    L['0']['1'] = BitArray(bin=extended_seed_0[sec_param + 1 : 2 * sec_param + 1])
    L_T['0']['1'] = BitArray(bin=extended_seed_0[2 * sec_param + 1])
    R['0']['0'] = BitArray(bin=extended_seed_0[2 * sec_param + 2 : 3 * sec_param + 2])
    R_T['0']['0'] = BitArray(bin=extended_seed_0[3 * sec_param + 2])
    R['0']['1'] = BitArray(bin=extended_seed_0[3 * sec_param + 3 : 4 * sec_param + 3])
    R_T['0']['1'] = BitArray(bin=extended_seed_0[4 * sec_param + 3])

    L['1']['0'] = BitArray(bin=extended_seed_1[:sec_param])
    L_T['1']['0'] = BitArray(bin=extended_seed_1[sec_param])
    L['1']['1'] = BitArray(bin=extended_seed_1[sec_param + 1 : 2 * sec_param + 1])
    L_T['1']['1'] = BitArray(bin=extended_seed_1[2 * sec_param + 1])
    R['1']['0'] = BitArray(bin=extended_seed_1[2 * sec_param + 2 : 3 * sec_param + 2])
    R_T['1']['0'] = BitArray(bin=extended_seed_1[3 * sec_param + 2])
    R['1']['1'] = BitArray(bin=extended_seed_1[3 * sec_param + 3 : 4 * sec_param + 3])
    R_T['1']['1'] = BitArray(bin=extended_seed_1[4 * sec_param + 3])

    #must be masked by random word
    
    CW = {'0' : {'S' : {'L' : {}, 'R' : {}}, 'T' : {'L' : {}, 'R' : {}}},
          '1' : {'S' : {'L' : {}, 'R' : {}}, 'T' : {'L' : {}, 'R' : {}}}}

    cryptogen = random.SystemRandom()
    random_seed = cryptogen.randrange(2 ** sec_param)
    # I get tons of zeros - need to change randomness creation
    randomness  = "{0:b}".format(prg(random_seed, 8)).zfill(8 * sec_param + 8)
    
    t0 = node.Tbit[0].bin
    t1 = node.Tbit[1].bin

    node.left_bit = BitArray(bin=node.left_bit)
    node.right_bit = BitArray(bin=node.right_bit)

    CW[t0]['S']['L'][(~node.left_bit).bin] = (L['1'][(~node.left_bit).bin] ^ BitArray(bin=randomness[:sec_param])).bin
    CW[t1]['S']['L'][(~node.left_bit).bin] = (L['0'][(~node.left_bit).bin] ^ BitArray(bin=randomness[:sec_param])).bin

    CW[t0]['T']['L'][(~node.left_bit).bin] = (L_T['1'][(~node.left_bit).bin] ^ BitArray(bin=randomness[sec_param])).bin
    CW[t1]['T']['L'][(~node.left_bit).bin] = (L_T['0'][(~node.left_bit).bin] ^ BitArray(bin=randomness[sec_param])).bin


    CW[t0]['S']['R'][(~node.right_bit).bin] = (R['1'][(~node.right_bit).bin] ^ \
                                       BitArray(bin=randomness[sec_param + 1 : 2 * sec_param + 1])).bin
    CW[t1]['S']['R'][(~node.right_bit).bin] = (R['0'][(~node.right_bit).bin] ^ \
                                       BitArray(bin=randomness[sec_param + 1 : 2 * sec_param + 1])).bin

    CW[t0]['T']['R'][(~node.right_bit).bin] = (R_T['1'][(~node.right_bit).bin] ^ \
                                        BitArray(bin=randomness[2 * sec_param + 1])).bin
    CW[t1]['T']['R'][(~node.right_bit).bin] = (R_T['0'][(~node.right_bit).bin] ^ \
                                        BitArray(bin=randomness[2 * sec_param + 1])).bin



    CW[t0]['T']['L'][node.left_bit.bin] = (L_T['1'][node.left_bit.bin] ^ \
                                          BitArray(bin=randomness[5 * sec_param + 2])).bin
    CW[t1]['T']['L'][node.left_bit.bin] = (L_T['0'][node.left_bit.bin] ^ \
                                          BitArray(bin=randomness[5 * sec_param + 2]) ^ BitArray(bin='1')).bin

    CW[t0]['T']['R'][node.right_bit.bin] = (R_T['1'][node.right_bit.bin] ^ \
                                           BitArray(bin=randomness[8 * sec_param + 3])).bin
    CW[t1]['T']['R'][node.right_bit.bin] = (R_T['0'][node.right_bit.bin] ^ \
                                           BitArray(bin=randomness[8 * sec_param + 3]) ^ BitArray(bin='1')).bin

    if node.left_child.is_leaf:
        CW[t0]['S']['L'][node.left_bit.bin] = (L['1'][node.left_bit.bin] ^ \
                                         BitArray(int=node.left_child.value,length=sec_param) ^ \
                                         BitArray(bin=randomness[2 * sec_param + 2 : 3 * sec_param + 2])).bin
        CW[t1]['S']['L'][node.left_bit.bin] = (L['0'][node.left_bit.bin] ^ \
                                         BitArray(bin=randomness[2 * sec_param + 2 : 3 * sec_param + 2])).bin
    else:
        CW[t0]['S']['L'][node.left_bit.bin] = BitArray(bin=randomness[3 * sec_param + 2 : 4 * sec_param + 2]).bin
        CW[t1]['S']['L'][node.left_bit.bin] = BitArray(bin=randomness[4 * sec_param + 2 : 5 * sec_param + 2]).bin


        node.left_child.seed = [(L['0'][node.left_bit.bin] ^ BitArray(bin=CW[t0]['S']['L'][node.left_bit.bin])).int,
                                (L['1'][node.left_bit.bin] ^ BitArray(bin=CW[t1]['S']['L'][node.left_bit.bin])).int]
        node.left_child.Tbit = [L_T['0'][node.left_bit.bin] ^ BitArray(bin=CW[t0]['T']['L'][node.left_bit.bin]),
                                L_T['1'][node.left_bit.bin] ^ BitArray(bin=CW[t1]['T']['L'][node.left_bit.bin])]

    if node.right_child.is_leaf:
        CW[t0]['S']['R'][node.right_bit.bin] = (R['1'][node.right_bit.bin] ^ \
                                          BitArray(int=node.right_child.value,length=sec_param) ^ \
                                          BitArray(bin=randomness[5 * sec_param + 3 : 6 * sec_param + 3])).bin
        CW[t1]['S']['R'][node.right_bit.bin] = (R['0'][node.right_bit.bin] ^ \
                                          BitArray(bin=randomness[5 * sec_param + 3 : 6 * sec_param + 3])).bin
    else:
        CW[t0]['S']['R'][node.right_bit.bin] = BitArray(bin=randomness[6 * sec_param + 3 : 7 * sec_param + 3]).bin
        CW[t1]['S']['R'][node.right_bit.bin] = BitArray(bin=randomness[7 * sec_param + 3 : 8 * sec_param + 3]).bin


        node.right_child.seed = [(R['0'][node.right_bit.bin] ^ BitArray(bin=CW[t0]['S']['R'][node.right_bit.bin])).int,
                                 (R['1'][node.right_bit.bin] ^ BitArray(bin=CW[t1]['S']['R'][node.right_bit.bin])).int]
        node.right_child.Tbit = [R_T['0'][node.right_bit.bin] ^ BitArray(bin=CW[t0]['T']['R'][node.right_bit.bin]),
                                 R_T['1'][node.right_bit.bin] ^ BitArray(bin=CW[t1]['T']['R'][node.right_bit.bin])]

    node.left_bit = node.left_bit.bin
    node.right_bit = node.right_bit.bin

    node.cw = CW

    # print CW['0']
    # print CW['1']
    # print '--------------'

