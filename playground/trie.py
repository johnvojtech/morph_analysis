#!python3
class Node:
    def __init__(self, children={}, parent=None, end=False):
        self.parent=parent
        self.children=children
        self.desc = 0
        self.word = end

class Trie:
    def __init__(self):
        self.root = Node()

    def insert(self, word):
        current = self.root
        for i in word:
            current.desc += 1
            if i in current.children.keys():
                current = current.children[i]
            else:
                new = Node(children=dict(), parent=current)
                current.children[i] = new
                current = new
                current.word=True

    def insert_reverse(self, word):
        self.insert(word[::-1])

    def find(self, word):
        current = self.root
        for i in word:
            if i in current.children.keys():
                current = current.children[i]
            else:
                return None
        if current.word:
            return current
        else:
            return None

    def contains(self, word):
        return self.find(word) is not None

    def delete(self, word):
        current = self.find(word)
        current.word = False
        if current is None:
            return
        while current.parent is not None:
            if current.desc == 1:
                child = current
                current = current.parent
                current.pop(char)
            else:
                current.desc -= 1
                current = current.parent
    
    def get_endings(self, depth=1):
        processed = [(self.root, depth, "")]
        endings = []
        while len(processed) > 0:
            current = processed[0]
            
            node = current[0]
            depth = current[1]
            ending = current[2]
            processed = processed[1:]
            if len(list(node.children.keys())) > 1:
                depth -= 1
            if depth > 0:
                for char in node.children.keys():
                    processed.append((node.children[char], depth, str(char) + ending))
            else:
                endings.append(ending)
            
        return endings

    def ending_segments(self, witness):
        processed = [(self.root, "")]
        endings = []
        while len(processed) > 0:
            current = processed[0]
            node = current[0]
            ending = current[1]
            processed = processed[1:]
            if node.desc >= witness:
                for char in node.children.keys():
                    e =  str(char) + ending
                    processed.append((node.children[char], e)) 
            else:
                endings.append(ending)
            
        return endings


def get_batch_endings(batch, depth):
    t = Trie()
    for word in batch:
        t.insert_reverse(word)
    return t.get_endings(depth=depth)

def get_ending_segments(batch, witness=10):
    t = Trie()
    for word in batch:
        t.insert_reverse(word)
    return t.ending_segments(witness)
