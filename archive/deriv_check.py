#!python3
import sys
import pickle
import math
from collections import defaultdict
import derinet.lexicon as dlex

lexicon = dlex.Lexicon()
lexicon.load('derinet-2-1.tsv')

root_lexemes = []
derived = []
compound = []

for lexeme in lexicon.iter_lexemes():
    #print(lexeme)
    if lexeme.parent == None:
        root_lexemes.append(lexeme.lemma.lower())
    else:
        derived.append(lexeme.lemma.lower())
    if any(rel.type == "Compounding" for rel in lexeme.parent_relations):
        for sub_lexeme in lexeme.iter_subtree():
            compound.append(sub_lexeme.lemma.lower())


with open(sys.argv[1], "r") as r:
     segments_b = [s.strip().split("\t") for s in r.readlines()]
segments = []
for segment in segments_b:
    if not any(s[1] == segment[1] for s in segments):
        segments.append(segment)

resolved = {"der":[], "root":[], "comp":[]}

for s in segments:
    der = ""
    inf = ""
    comp = ""
    #Derivation
    if s[0] in derived:
        der = "1"
    if s[0] in root_lexemes:
        der = "0"
    #Compounds
    if s[0] in compound:
        comp = "1"
    else:
        comp = "0"
    #Inflexion
    #Right type? (Substantive, Adjective, Pronoun, Number, Verb)
    #All inflected forms
    #Is substring of all inflected forms?
    #
    tag = inf+der+comp
    if len(tag) != 2:
        print("\t".join([s[0], s[1], s[2], tag]))
        if der == "1":
            resolved["der"].append(s)
        if der == "0":
            resolved["root"].append(s)
        if comp == "1":
            resolved["comp"].append(s)
    #else:
    #    print("\t".join(["N_UD", s[0], s[1], s[2], tag]))


#rint("Derivations: "+ str(len(resolved["der"])))
#rint("Root words: "+ str(len(resolved["root"])))
#rint("Compounds: " + str(len(resolved["comp"])))

