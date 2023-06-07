#!python3
import sys
import pickle
import math
from collections import defaultdict
import derinet.lexicon as dlex

lexicon = dlex.Lexicon()
lexicon.load('derinet/tools/data-api/derinet2/derinet-2-0.tsv')


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

def _get_segments(word):
    i = 0
    segments = []
    current = ""
    new = False
    while i < len(word):
        cur = word[i:i+1]
        if cur == "@":
            if not new:
                segments.append(current)
                current = ""
            current += word[i:i+2]
            new = True
            i += 2
        else:
            if new:
                if len(current) > 0:
                    segments.append(current)
                current = ""
                new=False
            current += word[i:i+1]
            i += 1
    if len(current) > 0:
        segments.append(current)
    return segments

def get_segments(word):
    segments = _get_segments(word)
    return [s.replace("@","") for s in segments]

def align(segments, inr):
    morphs = set([x for y in segments for x in y[1]])
    candidates = [morph for morph in morphs if all(any(morph in substr for substr in segword[0].lemma)for segword in segments)]
    new_parts = [morph for morph in morphs if any(all(morph not in substr for substr in segword[0].lemma)for segword in segments)]
    r_cand = [morph for morph in candidates if any(morph in parent_rc for parent_rc in inr)]
    return [], [], r_cand

def segment_node(lexemes, candidate_roots, prev_segm):
    if len(lexemes) == 0:
        return []
    lexeme = lexemes[0]
    children = lexeme.children
    lemma = lexeme.lemma.split("#")[0]

    shedit = [(child, shortest_edit(lemma, child.lemma))for child in children]
    deriword = [item[1][2] for item in shedit]
    segments = [(word[0], get_segments(word[1][2])) for word in shedit]
    #print("A")
    #print(segments)
    _, _, rcs = align(segments, candidate_roots)
    segm = shortest_edit("".join(prev_segm), lemma)[2]
    for item in prev_segm:
        segm = segm.replace(item, " " + item + " ").replace("@ " + item + " ", "@" + item)
   
    segm = segm.replace("@","")

    segmp = segm
    rc_set = set([item for item in rcs if item in lemma]) 
    if len(rc_set) > 0:
        root = max(rc_set, key=len)
    elif len(candidate_roots) > 0:
        root = max(candidate_roots, key=len)
    if len(root) > 0:
        segm = segm.replace(root, " (" + root + ") ", 1).strip()

    segm = [s for s in segm.split(" ") if len(s) > 0]
    print(segm)

    child_segments = [segm]
    for w in shedit:
        child = w[0]
        cs = segment_node([child], [root], segmp)
        child_segments += cs
    return child_segments

lexemes = lexicon.get_lexemes(lemma="dát")
segments = segment_node(lexemes, [lexemes[0].lemma.split("#")[0]], [lexemes[0].lemma.split("#")[0]])
for seg in segments:
    print(" ".join(seg))
