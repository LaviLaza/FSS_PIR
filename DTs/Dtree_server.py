

from bitstring import BitArray
from Dtree_prg import prg
import Queue


def Eval(x, tree_root, seed,  T, sec_param):

    tree_root.seed = seed
    tree_root.Tbit = T

    SUM = BitArray(int=0, length=sec_param)

    queue = Queue.Queue()
    queue.put(tree_root)

    while not queue.empty():
        node = queue.get()

        L = {}
        L_T = {}
        R = {}
        R_T = {}

        # zfill is actually a problem. I need to have random string not 0 fills...
        extended_seed = "{0:b}".format(prg(node.seed, 4)).zfill(4 * sec_param + 4)

        L['0'] = BitArray(bin=extended_seed[:sec_param])
        L_T['0'] = BitArray(bin=extended_seed[sec_param])
        L['1'] = BitArray(bin=extended_seed[sec_param + 1: 2 * sec_param + 1])
        L_T['1'] = BitArray(bin=extended_seed[2 * sec_param + 1])
        R['0'] = BitArray(bin=extended_seed[2 * sec_param + 2: 3 * sec_param + 2])
        R_T['0'] = BitArray(bin=extended_seed[3 * sec_param + 2])
        R['1'] = BitArray(bin=extended_seed[3 * sec_param + 3: 4 * sec_param + 3])
        R_T['1'] = BitArray(bin=extended_seed[4 * sec_param + 3])

        S_L = L[x[node.index]] ^ BitArray(bin=node.cw[node.Tbit]['S']['L'][x[node.index]])
        S_R = R[x[node.index]] ^ BitArray(bin=node.cw[node.Tbit]['S']['R'][x[node.index]])


        if node.left_child.is_leaf:
            SUM ^= S_L
        else:
            T_L = L_T[x[node.index]] ^ BitArray(bin=node.cw[node.Tbit]['T']['L'][x[node.index]])
            node.left_child.seed = S_L.int
            node.left_child.Tbit = T_L.bin
            queue.put(node.left_child)

        if node.right_child.is_leaf:
            SUM ^= S_R
        else:
            T_R = R_T[x[node.index]] ^ BitArray(bin=node.cw[node.Tbit]['T']['R'][x[node.index]])
            node.right_child.seed = S_R.int
            node.right_child.Tbit = T_R.bin
            queue.put(node.right_child)

    return SUM.bin
