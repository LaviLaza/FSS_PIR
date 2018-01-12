"""
PRG module
Description: The module utilizes Python's random bit generation function as a PRG.
Author: Lavi. Lazarovitz
Date: 10/1/18

"""

import random

def prg(seed):

    """The function is used as a Pseudo-Random Generator. It will extend the length of the seed to 2*seed + 2.

    Args:
        seed (int): the seed for the PRG.

    Returns:
        long: The return value is a pseudo-random long number.

    TODO: The getrandbits used in this function shouldn't be used in production for security reasons.
          The getransbits should be replaced with secure PRG.

    """
    # Setting the seed
    random.seed(seed)

    # Returning 2*(seed's length)  + 2 pseudo random bits
    return random.getrandbits(2*(seed.bit_length()) + 2)

if __name__ == "__main__":
   print prg(100)