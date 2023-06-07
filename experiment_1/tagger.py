#!python3
import sys
from nltk.tag import CRFTagger

def prepare_training_data(filename):
    with open(filename, "r+") as r:
        x = []
        for line in r:
            xw = []
            for item in line.split():
                if len(item) > 0:
                    if "(" in item:
                        xw.append((item.replace("(", "").replace(")", ""), "R"))
                    else:
                        xw.append((item, "A"))
            x.append(xw)
        return x

training_data = prepare_training_data(sys.argv[1])
test_data = [line.strip().split() for line in open(sys.argv[2], "r")]
ct = CRFTagger()
ct.train(training_data,'model.crf.tagger')
tagged = ct.tag_sents(test_data)
for t in tagged:
    word = [x[0] for x in t]
    tags = [x[1] for x in t]
    print(" ".join(word) + "\t" + "".join(tags))               
