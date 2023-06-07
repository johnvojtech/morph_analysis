#!python3
import pickle
import sys

with open(sys.argv[1], "rb") as r:
    vw = pickle.load(r)
    print(len(list(vw.keys())))
