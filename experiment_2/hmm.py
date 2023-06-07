import sys
from nltk.tag.hmm import HiddenMarkovModelTrainer

unsuper_data = [["#"] + line.strip().split() for line in open(sys.argv[1], "r")]
super_data = [list(zip(["#"] + line.strip().split()[:-1], "#" + line.strip().split()[-1])) for line in open(sys.argv[2], "r")]
test_data =  [["#"] + line.strip().split()for line in open(sys.argv[3], "r")]
states = ["R","P","S","I","N","O"]
symbols = list(set([x for y in unsuper_data + test_data for x in y]))
#print(super_data[:10])
#print(unsuper_data[:10])
symbols.sort()
#print(symbols)
#print(any("p" == x for x in unsuper_data))
unsuper_data = []
model = HiddenMarkovModelTrainer(states, symbols).train(super_data, unsuper_data)
for item in test_data:
    print(" ".join(item) + "\t" +"".join(model.best_path(item)))

