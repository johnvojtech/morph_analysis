import sys
from bi_lstm_crf.app import WordsTagger


model = WordsTagger(model_dir=sys.argv[1])
test_data = [line.strip().split() for line in open(sys.argv[2], "r")]
for word in test_data:
    tags, sequences = model([word])
    print(" ".join(word) + "\t" + "".join(tags[0]))
