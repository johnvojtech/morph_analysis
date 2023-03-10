#!python3
import sys
import pickle
import derinet.lexicon as dlex
import utils.preprocessing as dp

lexicon = dlex.Lexicon()
lexicon.load('derinet/tools/data-api/derinet2/derinet-2-0.tsv')
roots = [lexeme.lemma.lower() for lexeme in lexicon.iter_trees()]
with open("data/old_sigmorphon22/form_lemma.pickle", "rb") as r:
    form_lemma = pickle.load(r)

def load_data(filename, column=0):
    with open(filename, "r+") as r:
        data = [s.strip().split("\t")[column].split() for s in r.readlines()]
        return data


def get_signature(word, backup):
    def check(parameters, signature = ""):
        for parameter in parameters:
            if parameter:
                signature += "1"
            else:
                signature += "0"
        return signature

    lemma = form_lemma["".join(word)]
    lexeme = lexicon.get_lexemes(lemma=lemma)
    if len(lexeme) > 0:
        is_root = "is_compound" not in lexeme[0].misc.keys() and len(lexeme[0].all_parents) == 0
        parameters = [is_root, not is_root, "".join(word) != lemma, "is_compound" in lexeme[0].misc.keys()]
    else:
        signature = ""
        parameters = ["P" not in signature and "S" not in signature, "P" in signature or "S" in signature, "".join(word) != lemma, signature.count("R") > 1]
    return(check(parameters))

data=load_data(sys.argv[1], 0)
signatures=load_data(sys.argv[1], 1)
#_,_,_ = dp.lemmatize(data)
for word in data:
    print(" ".join(word) + "\t" + get_signature(word, signatures6666))
