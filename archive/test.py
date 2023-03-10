#!python3
import derinet.lexicon as dlex
import pickle

lexicon = dlex.Lexicon()
lexicon.load("UDer-1.0/pt-NomLexPT/UDer-1.0-pt-NomLexPT.tsv")



def find_origin(lemma):
    lexemes = lexicon.get_lexemes(lemma=lemma)
    for lexeme in lexemes:
        print(lexeme.segmentation)
        root = lexeme.get_tree_root()
        print(root.lemma)

annotated = []
for lexeme in lexicon.iter_lexemes():
    for segment in lexeme.segmentation:
        if segment["Type"] == "Root":
            annotated.append(lexeme)
            print(lexeme.segmentation)

print(len(annotated))
with open("es_DeriNetES.pickle", "wb") as writer:
    pickle.dump(annotated, writer)
