from cy_anneal import *

if __name__ == '__main__':
    state = []
    new_state, e = anneal(state, 100000, 4, 1000000)

    new_state.sort()
    print "['103225', '103386', '103470', '103633', '103650', '103653', '103665', '95534']"
    print "^^^^^ previously ^^^"
    print new_state, e

