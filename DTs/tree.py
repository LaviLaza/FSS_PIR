
from bitstring import BitArray

class Node:
    def __init__(self,  left_bit = None, right_bit = None,seed = None, Tbit = None, index = None, is_leaf = False, value = 0):
        self.seed = seed
        self.Tbit = Tbit

        # index should be a number starting at 0 (must be set for none leaf nodes
        self.index = index
        self.is_leaf = is_leaf
        # if the node os leaf, the value should be an int
        self.value = value

        # Value must be less than 2^sec_param

        self.right_child = None
        self.left_child = None

        # bit should be single bit string
        if left_bit is not None:
            self.left_bit = left_bit
        if right_bit is not None:
            self.right_bit = right_bit

        self.cw = None

    def set_R_child(self, obj):
        self.right_child = obj

    def set_L_child(self, obj):
        self.left_child = obj


