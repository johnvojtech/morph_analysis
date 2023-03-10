#!python3
import sys
import pickle
import math
from collections import defaultdict
import utils.preprocessing as dp

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

def fit_lemmas(lemma1, lemma2):
    shed = shortest_edit(lemma1, lemma2)
    ls = shed[2].split("@#")
    ls2 = []
    for i in range(len(ls)):
        item = ls[i]
        if 2 * item.count("@") >= len(item):
            ls2.append((item.replace("@", ""), i))
    return(ls2)


def c_e(p_ij, p_j):
    if p_ij > 0 and p_j > 0:
        return p_ij*math.log(p_ij/p_j)
    return 0

def statistics(data, name, lexicon):
    form_lemma, _, _, _ = dp.lemmatize(data, name)
    def ce_s(p_ij, p_j):
        return p_ij * math.log(p_ij/p_j)

    bigrams = defaultdict(lambda:defaultdict(int))
    N = 0
    for word in data:
        word_2 = ["<S>"] + word + ["<E>"]
        for i in range(len(word_2) - 1):
            bigrams[word_2[i]][word_2[i+1]] += 1
            N += 1

    morphs = list(set([morph for word in data for morph in word]))
    morph_stats = {}
    """
    depths = defaultdict(list)
    for root in lexicon.iter_trees():
        morphs_check = morphs.copy()
        lexemes = [root]
        depth = 0
        while len(lexemes) > 0:
            lemmas = [lexeme.lemma for lexeme in lexemes]
            for morph in morphs_check:
                if any(morph in lemma for lemma in lemmas):
                    depths[morph].append(depth)
                    morphs_check.remove(morph)
            lexemes = [x for y in [lexeme.children for lexeme in lexemes] for x in y]
            depth += 1
        for morph in morphs:
            depths[morph].append(depth)

    left_counts = {morph:sum([bigrams[morph][j] for j in bigrams[morph].keys()]) for morph in morphs}
    right_counts = {morph:sum([bigrams[i][morph] for i in bigrams.keys()]) for morph in morphs}
    """
    for morph in morphs:
        cont = [word for word in data if morph in word]
        freq = len(cont) / len(data)
        length = len(morph)
        """
        avg_depth = sum(depths[morph])/(len(depths[morph]) + 1)

        entropy_left = - sum([c_e(bigrams[i][morph]/N, right_counts[morph]/N) for i in bigrams.keys()])
        entropy_right = - sum([c_e(bigrams[morph][j]/N, left_counts[morph]/N) for j in bigrams.keys()])
        """
        morph_stats[morph] = (length, freq) #, 2**(entropy_left+entropy_right), avg_depth)

    return morphs, morph_stats
