#!python3
import sys
from collections import defaultdict

post = defaultdict(lambda: defaultdict(int))
with open(sys.argv[1], "r") as r:
     for line in r:
         w_t = line.strip().split("\t")
         word = w_t[0].split()
         tag = w_t[1]
         for i in range(len(word)):
             post[word[i]][tag[i:i+1]] += 1

with open(sys.argv[2], "r") as r:
    for line in r:
        word = line.strip().split()
        tag = ""
        for morph in word:
            if len(list(post[morph].keys())) > 0:
                tag += max(list(post[morph].keys()), key = lambda x: post[morph][x])
            else:
                tag += "R"
        print(" ".join(word) + "\t" + tag)
