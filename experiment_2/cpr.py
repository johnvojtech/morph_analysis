#!python3
import sys

with open(sys.argv[1], "r") as r:
    test = [line.strip().split() for line in r]
with open(sys.argv[2], "r") as r:
    gold = [line.strip().split() for line in r]

TP = 0
FP = 0
TN = 0
FN = 0
C = 0
accw = 0
for t, g in zip(test, gold):
    for i in range(len(t)):
        ts = t[i:i+1]
        gs = g[i:i+1]
        acc = True
        if ts == gs and ts[:1] == "(":
            TP += 1
        elif ts == gs and ts[:1] != "(":
            TN += 1
        elif ts != gs and ts[:1] == "(":
            FP += 1
            acc = False
        elif ts != gs and ts[:1] != "(":
            FN += 1
            acc = False
        C += 1
        if acc:
            accw += 1

#precision = TP/(TP + FP)
#recall = TP/(TP + FN)
#F = (2*precision*recall)/(precision+recall)
print((TP + TN)/C)
#print(precision)
#print(recall)
#print(F)
#print(accw/C)
