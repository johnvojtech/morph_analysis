#!python3
import sys
import pickle
import math
from collections import defaultdict
import derinet.lexicon as dlex

lexicon = dlex.Lexicon()
lexicon.load('derinet/tools/data-api/derinet2/derinet-2-0.tsv')

def r_4(word, morph_stats):
    viable = [m for m in word if m in morph_stats.keys()]
    ms = [sum([morph_stats[x][i] for x in viable]) for i in range(3)]
    rts = min(viable, key = lambda x: sum([morph_stats[x][i]/(ms[i] + 0.00000000001) for i in [0,1,2]]))
    return [(rts, word.index(rts))]

def shortest_edit(w1, w2):
    known = defaultdict(lambda: defaultdict(int))
    strout = ""
    for i in range(len(w1)):
        known[i][-1] = i+1
    for j in range(len(w2)):
        known[-1][j] = j+1
    for i in range(len(w1)):
         for j in range(len(w2)):
             a = known[i-1][j-1]
             if w1[i] != w2[j]:
                 a += 1
             b = known[i][j-1]+1
             c = known[i-1][j]+1
             res = min([a,b,c])
             known[i][j] = res
    x = i
    y = j
    while x > -1 or y > -1:
        a = known[x-1][y-1]
        b = known[x-1][y]
        c = known[x][y-1]
        res = min([a,b,c])
        if res == a and x > -1 and y > -1:
            strout = w2[y] + strout
            x -= 1
            y -= 1
            if w1[x+1] != w2[y+1]:
                strout = "@" + strout
        elif (res == b and b > c)or y < 0:
            x -= 1
        else:
            strout = "@" + w2[y] + strout
            y -= 1
    return [w2, known[i][j], strout]

def good(schema, shortest, lemmas):
    """lemma contains the substring specified by "schema", "shortest" """
    OK = True
    for lemma in lemmas:
        OK = any(all(lemma[j + i] == shortest[i] for i in schema) for j in range(-schema[0], len(lemma) - schema[-1]))
        if not OK:
            return False
    return True

def variants(schema, shortest, lemmas):
    """generates possible variants of the schema"""
    schemata = []
    start = 0
    if len(schema)>0:
        start = schema[-1] + 1
    for j in range(start, len(shortest)):
        new_schema = schema + [j]
        if good(new_schema, shortest, lemmas):
            schemata.append(new_schema)
    return(schemata)

#def prune(schemata, m):
#    """groups schemata ending on the same position, returns the longest one"""
#    grouped = [[schema for schema in schemata if schema[-1] == i] for i in range(m)]
#    return [max(i_schemata, key=len) for i_schemata in grouped if len(i_schemata) > 0]

def get_schemata(lemmas):
    """for lemmas, returns longest common substring (with wildcards)"""
    shortest = min(lemmas, key=len)
    schemata = [[]]
    max_len = -1
    new_max = 0
    new = []
    while(max_len < new_max):
        max_len = new_max
        for schema in schemata.copy():
            new_schemata = variants(schema, shortest, lemmas)
            if len(new_schemata) > 0 and schema in schemata:
                schemata.remove(schema)
            schemata = schemata + new_schemata
        if len(schemata[0]) == 0:
            return []
        #chemata = prune(schemata, len(shortest))
        new_max = len(max(schemata, key=len))

    schemata = [schema for schema in schemata if len(schema) == max_len]
    return [[(i - schema[0], shortest[i]) for i in schema] for schema in schemata]

def agrees(morph, schema):
    return any(all(morph[item[0] + j] == item[1] for item in schema) for j in range(len(morph) - schema[-1][0]))

def similarity(morph, schema):
    return min([0] + [sum([int(morph[item[0] + j] == item[1]) for item in schema]) for j in range(len(morph) - schema[-1][0])])

def subtree(lexeme, changes=1):
    r = lexeme
    while r.parent is not None and len(get_schemata([r.parent.lemma, r.lemma])) > len(r.lemma) - changes:
        r = r.parent
    return r

def roots(word, morph_stats):
    viable = [m for m in word if m in morph_stats.keys()]
    lexemes = lexicon.get_lexemes(lemma="".join(word))
    if len(lexemes) == 0:
       return r_4(word, morph_stats)
    root = lexemes[0].get_tree_root()
    lemmas = [child.lemma.lower() for child in root.iter_subtree()]
    schemata = get_schemata(lemmas)
    candidates = []
    if len(schemata) > 0:
        candidates = [seg for seg in word if any(agrees(seg, schema) for schema in schemata)]
    if len(candidates) == 0:
        candidates = viable
    ws = [root.lemma] + [lex.lemma for lex in root.children]

    scored = {x: sum([shortest_edit(x, c)[1] for c in ws]) for x in word}
    snorm = sum(scored.values())
    viable = candidates
    ms = [sum([morph_stats[x][i] for x in viable]) for i in range(3)]
    minm = min(viable, key = lambda x: scored[x]/(snorm + 0.00000000001) + sum([morph_stats[x][i]/(ms[i] + 0.00000000001) for i in [0,1,2]]))
    return  [(minm, word.index(minm))]
