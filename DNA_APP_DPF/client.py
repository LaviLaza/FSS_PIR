from constants import constant
import logging
from errors import InvalidDNAException
from keygen import gen
from bitstring import BitArray





class DNA_App_Client:

    def __init__(self, dna_string):
        self.dna_string = dna_string.upper().strip()

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

    def build_function(self):


        return gen(constant.SEC_PARAM, self.dna_bitstring)