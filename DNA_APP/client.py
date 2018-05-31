
# accept DNA string
# convert the DNA to bitstring
# build trees - based on rich simple tree with several combinations of locations
# send to client

# add the corresponding values of the arrays
# get trees from app
# send trees to servers
    #need to know the servers IP address

# receive array back from servers
# send array to app

from constants import constant
import logging
from errors import InvalidDNAException
import random
from bitstring import BitArray
import Queue
from DTs.tree import Node
from DTs.Dtree_gen import generate_DT


class DNA_App_Client:

    def __init__(self, dna_string):
        self.dna_string = dna_string.upper()

        if not self.check_valid_dna_string():
            raise InvalidDNAException("Invalid DNA input string")
        else:
            logging.info("DNA string is valid.")

        self.dna_bitstring = self.convert_dna_to_bitstring()

    def check_valid_dna_string(self):

        return all(i in constant.valid_dna for i in self.dna_string)

    def convert_dna_to_bitstring(self):

        dna_bitstring = self.dna_string.replace('A',constant.DNA_DICT['A'])
        dna_bitstring = dna_bitstring.replace('C',constant.DNA_DICT['C'])
        dna_bitstring = dna_bitstring.replace('G', constant.DNA_DICT['G'])
        dna_bitstring = dna_bitstring.replace('T', constant.DNA_DICT['T'])


        return dna_bitstring

    def build_d_distance_trees(self, distance):
        # The leaf values at every path resulting in a DNA string with distance less than d
        # The trees support a single match on the server side - requires modifications to checks.json

        queue = Queue.Queue()

        coin = self.flip_coin()

        tree_root = Node(index=0, is_leaf=False, left_bit=coin.bin, right_bit=(~coin).bin, value=0)

        queue.put(tree_root)

        while not queue.empty():

            current_node = queue.get()

            #print "current index: %d,  max length: %d" % (current_node.index, len(self.dna_bitstring))

            left_coin = self.flip_coin()
            right_coin = self.flip_coin()

            left_true_path_flag = True
            right_true_path_flag = True

            left_value = current_node.value
            right_value = current_node.value

            if not current_node.left_bit == self.dna_bitstring[current_node.index]:
                left_true_path_flag = False
                if current_node.index % 2:
                    left_value += 1
            elif not current_node.true_path_flag and current_node.index % 2:
                left_value += 1

            if not current_node.right_bit == self.dna_bitstring[current_node.index]:
                right_true_path_flag = False
                if current_node.index % 2:
                    right_value += 1
            elif not current_node.true_path_flag and current_node.index % 2:
                right_value += 1

            left_node = Node(index=current_node.index + 1, is_leaf=False, left_bit=left_coin.bin,
                             right_bit=(~left_coin).bin, value=left_value,
                             true_path_flag=left_true_path_flag)
            right_node = Node(index=current_node.index + 1, is_leaf=False, left_bit=right_coin.bin,
                              right_bit=(~right_coin).bin, value=right_value,
                              true_path_flag=right_true_path_flag)

            if current_node.index == (len(self.dna_bitstring) - 1):
                left_node.value = 1
                right_node.value = 1

                left_node.is_leaf = True
                right_node.is_leaf = True

            if left_value > distance:
                left_node.value = 0
                left_node.is_leaf = True
            if right_value > distance:
                right_node.value = 0
                right_node.is_leaf = True

            current_node.set_L_child(left_node)
            current_node.set_R_child(right_node)

            if not left_node.is_leaf:
                queue.put(current_node.left_child)
            if not right_node.is_leaf:
                queue.put(current_node.right_child)

            current_node.value = 0

        root = generate_DT(tree_root, constant.SEC_PARAM)
        return self.clean_tree(root)


    def build_secret_share_trees(self):

        # extract the current bit and push the root to the queue
        # run until the queue is empty - pop the first node
        # flip a coin to decide weather to go left or right with the right bit
        # create the node and set his left and right childs + set the accuracy ratio for each child
        # delete the accuracy value of the current node
        # push each of the childs to the queue
        # if there are no more bits - the next level should be leafs - set the leaf and the accuracy ratio as value

        queue = Queue.Queue()

        coin = self.flip_coin()

        tree_root = Node(index=0, is_leaf=False, left_bit=coin.bin, right_bit=(~coin).bin, value=0)

        queue.put(tree_root)

        while not queue.empty():


            current_node = queue.get()

            #print "current index: %d,  max length: %d" % (current_node.index, len(self.dna_bitstring))

            left_coin = self.flip_coin()
            right_coin = self.flip_coin()

            left_true_path_flag = False
            right_true_path_flag = False


            if current_node.left_bit == self.dna_bitstring[current_node.index]:
                left_true_path_flag = True
                if (current_node.index % 2) and current_node.true_path_flag:
                    left_value = current_node.value + 2
                else:
                    left_value = current_node.value

                right_value = current_node.value
            else:
                right_true_path_flag = True
                if (current_node.index % 2) and current_node.true_path_flag:
                    right_value = current_node.value + 2
                else:
                    right_value = current_node.value

                left_value = current_node.value

            left_node = Node(index=current_node.index + 1, is_leaf=False, left_bit=left_coin.bin,
                                          right_bit=(~left_coin).bin, value=left_value,
                                            true_path_flag=left_true_path_flag)
            right_node = Node(index=current_node.index + 1, is_leaf=False, left_bit=right_coin.bin,
                                          right_bit=(~right_coin).bin, value=right_value,
                                          true_path_flag=right_true_path_flag)

            if current_node.index == (len(self.dna_bitstring) - 1):
                left_node.value = int(round(float(left_node.value) / len(self.dna_bitstring),2) * 100)
                right_node.value = int(round(float(right_node.value) / len(self.dna_bitstring),2) * 100)

                left_node.is_leaf = True
                right_node.is_leaf = True

            current_node.set_L_child(left_node)
            current_node.set_R_child(right_node)

            if not left_node.is_leaf and not right_node.is_leaf:
                queue.put(current_node.left_child)
                queue.put(current_node.right_child)

            current_node.value = 0

        root = generate_DT(tree_root,constant.SEC_PARAM)

        return self.clean_tree(root)

    def flip_coin(self):
        sysrand = random.SystemRandom()
        return BitArray(bin=str(int(round(sysrand.random()))))

    def clean_tree(self,root):

        seed0 = root.seed[0]
        seed1 = root.seed[1]
        root.seed = None

        return root,seed0,seed1
