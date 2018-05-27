from Dtree_gen import generate_DT
from Dtree_server import Eval
from tree import Node
from bitstring import BitArray


def main():
    tree_root = Node(index=0,is_leaf=False,left_bit='0',right_bit='1')
    tree_root.set_L_child(Node(is_leaf=True,value=9))
    tree_root.set_R_child(Node(index=1,is_leaf=False,left_bit='1',right_bit='0'))

    v2 = tree_root.right_child
    v2.set_L_child(Node(is_leaf=True,value=11))
    v2.set_R_child(Node(is_leaf=True,value=13))


    secret_shared_tree = generate_DT(tree_root,sec_param=10)
    seed0 = secret_shared_tree.seed[0]
    seed1 = secret_shared_tree.seed[1]
    secret_shared_tree.seed = None

    SUM_0 = Eval(x='10', tree_root=secret_shared_tree, seed=seed0, T=BitArray(bin='0'), sec_param=10)
    SUM_1 = Eval(x='10', tree_root=secret_shared_tree, seed=seed1, T=BitArray(bin='1'), sec_param=10)

    SUM = (SUM_0 ^ SUM_1).int

    print SUM


if __name__ == "__main__":
    main()
