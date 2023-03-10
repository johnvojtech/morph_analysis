import sys
import pickle
with open(sys.argv[1], "rb") as r:
    d = pickle.load(r)
    print(len(list(d.keys())))
    print(list(d.keys())[-10:])
    #print(list(d.values())[-10:])
