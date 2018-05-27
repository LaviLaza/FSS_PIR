from dt_keygen import gen
from dt_server import eval


def main():
    k0,k1 = gen(10,'10111')
    # print k0
    # print k1

    e0 = eval('0',k0,'11111',10)
    e1 = eval('1',k1,'11111',10)

    print e0
    print e1


    # If both arrays are equal than the value is out of range
    if e0 == e1:
        print "Final output is 0"
    else:
        print "final output is 1"

if __name__ == "__main__":
    main()