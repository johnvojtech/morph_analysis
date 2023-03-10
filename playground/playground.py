#!python3
import sys
import pickle
import math
from collections import defaultdict
import derinet.lexicon as dlex

lexicon = dlex.Lexicon()
lexicon.load('derinet-2-0.tsv')
with open("data/form_lemma.pickle","rb") as r:
    form_lemma = pickle.load(r)

def statistics(data):
    def c_e(p_ij, p_j):
        if p_ij == 0:
            return 0
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

    depths = defaultdict(list)
    trees = defaultdict(list)
    for word in data:
        lexeme = lexicon.get_lexemes(lemma=form_lemma["".join(word)])
        lexemes = []
        if len(lexeme) > 0:
            for lex in lexeme:
                lexemes.append(lex.get_tree_root())
        depth = 0
        word_copy = word.copy()
        while len(lexemes) > 0:
            lemmas = [lexeme.lemma for lexeme in lexemes]
            for morph in word_copy:
                if any(morph in lemma for lemma in lemmas):
                    lemma = [x for x in lemmas if morph in x][0]
                    depths[morph].append((depth + max(0, (len(lemma) - len(morph))/2)))
                    word_copy.remove(morph)
            lexemes = [x for y in [lexeme.children for lexeme in lexemes] for x in y]
            depth += 1

    left_counts = {morph:sum([bigrams[morph][j] for j in bigrams[morph].keys()]) for morph in morphs}
    right_counts = {morph:sum([bigrams[i][morph] for i in bigrams.keys()]) for morph in morphs}
    for morph in morphs:
        cont = [word for word in data if morph in word]
        freq = len(cont) / len(data)
        length = len(morph)
        #vg_depth = sum(depths[morph])/(len(depths[morph]) + 1)

        entropy_left = - sum([c_e(bigrams[i][morph]/N, right_counts[morph]/N) for i in bigrams.keys()])
        entropy_right = - sum([c_e(bigrams[morph][j]/N, left_counts[morph]/N) for j in bigrams.keys()])
        morph_stats[morph] = (length, freq, max(entropy_left, entropy_right), depths[morph])
    return morphs, morph_stats


def EM(morphs, stats):
    old_lambdas = [0.5, 0.5, 0, 0]
    lambdas = [0.25, 0.25, 0.25, 0.25]
    epsilon = 0.00005
    mc = 10
    while mc > 0 and any(abs(lambdas[i] - old_lambdas[i]) > epsilon for i in range(len(lambdas))):
        for morph in morphs:
            ms = stats[morph]
            #is_root = lambdas[0] * ms[0] + lambdas[1] * 1/stats[2] + lambdas[3] * stats[3] + lambdas[4] * (sum(stats[4])/len(stats[4] + 1))
            


with open(sys.argv[1], "r") as r:
    data = [s.lower().strip().split("\t")[3].split()  for s in r]
    morphs, morph_stats = statistics(data)
    lambdas = [1, 1, 1, 1]
    for word in data:
        out = ""
        max_w = 0
        mw = []
        for i in range(len(word)):
            morph = word[i]
            stats = morph_stats[morph]
            is_root = (1/stats[0], stats[1], stats[2], sum(stats[3])/(len(stats[3]) + 1))
            mw.append((is_root, morph, i))
        
        mws = [mw.copy() for i in range(4)]
        for i in range(4):
            mws[i].sort(key = lambda x: x[0][i])

        mw = []
        min_w = 10000
        for i in range(len(word)):
            indices = [ls.index(x) for ls in mws for x in ls if x[2]== i]
            morph = word[i]
            value = lambdas[0] * indices[0] + lambdas[1] * indices[1] + lambdas[1]* indices[1] + lambdas[3] * indices[3]
            print(morph)
            print(indices)
            print(value)
            print()
            mw.append((value, morph))
            if value < min_w:
                min_w = value
        for item in mw:
            is_root = item[0]
            morph = item[1]
            if is_root <= min_w:
                out += "(" + morph + ") "
            else:
                out += morph + " "
        print(out.strip())
