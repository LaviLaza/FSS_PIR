import random
from bitstring import BitArray

def prg(seed):
    random.seed(seed)
    return random.getrandbits(2*(seed.bit_length()) + 2)


def gen(sec_param, a):
    cryptogen = random.SystemRandom()
    # TODO: Check the values are different
    S_0 = seed_srv_0 = cryptogen.randrange(2 ** sec_param)
    S_1 = seed_srv_1 = cryptogen.randrange(2 ** sec_param)

    K_0 = {'seed': S_0}
    K_1 = {'seed': S_1}

    T_srv_0 = BitArray(bin='0')
    T_srv_1 = BitArray(bin='1')

    tree_depth = len(a)

    for i in xrange(tree_depth):
        Sl_Tl_Sr_Tr_0 = "{0:b}".format(prg(seed_srv_0)).zfill(2 * sec_param + 2)
        Sl_Tl_Sr_Tr_1 = "{0:b}".format(prg(seed_srv_1)).zfill(2 * sec_param + 2)

        #       Left = 0, Right = 1
        S_T = {'0': {'0': {}, '1': {}}, '1': {'0': {}, '1': {}}}

        S_T['0']['0']['S'] = BitArray(bin=Sl_Tl_Sr_Tr_0[:sec_param])
        S_T['0']['0']['T'] = BitArray(bin=Sl_Tl_Sr_Tr_0[sec_param])
        S_T['0']['1']['S'] = BitArray(bin=Sl_Tl_Sr_Tr_0[sec_param + 1: 2 * sec_param + 1])
        S_T['0']['1']['T'] = BitArray(bin=Sl_Tl_Sr_Tr_0[2 * sec_param + 1])

        S_T['1']['0']['S'] = BitArray(bin=Sl_Tl_Sr_Tr_1[:sec_param])
        S_T['1']['0']['T'] = BitArray(bin=Sl_Tl_Sr_Tr_1[sec_param])
        S_T['1']['1']['S'] = BitArray(bin=Sl_Tl_Sr_Tr_1[sec_param + 1: 2 * sec_param + 1])
        S_T['1']['1']['T'] = BitArray(bin=Sl_Tl_Sr_Tr_1[2 * sec_param + 1])

        Keep_Lose = BitArray(bin=a[i])
        S_cw = S_T['0'][(~Keep_Lose).bin]['S'] ^ S_T['1'][(~Keep_Lose).bin]['S']

        T_cw = {}
        T_cw['0'] = S_T['0']['0']['T'] ^ S_T['1']['0']['T'] ^ Keep_Lose ^ BitArray(bin='1')
        T_cw['1'] = S_T['0']['1']['T'] ^ S_T['1']['1']['T'] ^ Keep_Lose

        K_0[i] = {'CW': S_cw, '0': T_cw['0'], '1': T_cw['1']}
        K_1[i] = {'CW': S_cw, '0': T_cw['0'], '1': T_cw['1']}

        seed_srv_0 = (S_T['0'][Keep_Lose.bin]['S'] ^ \
                                                BitArray(bin=((S_cw * abs(T_srv_0.int)).bin).zfill(sec_param))).int
        seed_srv_1 = (S_T['1'][Keep_Lose.bin]['S'] ^ \
                                                BitArray(bin=((S_cw * abs(T_srv_1.int)).bin).zfill(sec_param))).int


        T_srv_0 = S_T['0'][Keep_Lose.bin]['T'] ^ \
                                                BitArray(bin=((T_cw[Keep_Lose.bin] * abs(T_srv_0.int)).bin).zfill(1))
        T_srv_1 = S_T['1'][Keep_Lose.bin]['T'] ^ \
                                                BitArray(bin=((T_cw[Keep_Lose.bin] * abs(T_srv_1.int)).bin).zfill(1))


    return K_0, K_1


def eval(b,K,x,sec_param):
    seed = K['seed']
    T_bit = BitArray(bin=b)
    cur_item = None

    tree_depth = len(x)

    for i in xrange(tree_depth):
        Sl_Tl_Sr_Tr = "{0:b}".format(prg(seed)).zfill(2 * sec_param + 2)
        S_T = {'0': {}, '1': {}}

        S_T['0']['S'] = BitArray(bin=Sl_Tl_Sr_Tr[:sec_param])
        S_T['0']['T'] = BitArray(bin=Sl_Tl_Sr_Tr[sec_param])
        S_T['1']['S'] = BitArray(bin=Sl_Tl_Sr_Tr[sec_param + 1: 2 * sec_param + 1])
        S_T['1']['T'] = BitArray(bin=Sl_Tl_Sr_Tr[2 * sec_param + 1])

        S = {}
        T = {}

        S['0'] = S_T['0']['S'] ^ BitArray(bin=((K[i]['CW'] * abs(T_bit.int)).bin).zfill(sec_param))
        S['1'] = S_T['1']['S'] ^ BitArray(bin=((K[i]['CW'] * abs(T_bit.int)).bin).zfill(sec_param))
        T['0'] = S_T['0']['T'] ^ BitArray(bin=((K[i]['0'] * abs(T_bit.int)).bin).zfill(1))
        T['1'] = S_T['1']['T'] ^ BitArray(bin=((K[i]['1'] * abs(T_bit.int)).bin).zfill(1))

        cur_item = S[T_bit.bin]
        seed = S[T_bit.bin].int
        T_bit = T[T_bit.bin]

    return cur_item

if __name__ == "__main__":
    print gen(10, '1010')