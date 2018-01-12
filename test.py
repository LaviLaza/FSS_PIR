from keygen import gen
from server import eval
import server

def main():
    k0,k1 = gen(10,'1010')
    # print k0
    # print k1

    e0 = eval('0',k0,'1011',10)
    e1 = eval('1',k1,'1011',10)

    print e0
    print e1

if __name__ == "__main__":
    main()