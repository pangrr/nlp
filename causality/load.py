import yaml

def constructor (loader, node):
    fields = loader.construct_mapping(node)
    return Sentence(**fields)

class Sentence(object):
    def __init__ (self, e1Index, e1Nominal, e2Index, e2Nominal, to, lemma, words, roots, incomingEdges, outgoingEdges, sentence):
        self.e1Index = e1Index
        self.e2Nominal = e1Nominal
        self.e2Index = e2Index
        self.e2Nominal = e2Nominal
        self.to = to
        self.lemma = lemma
        self.words = words
        self.roots = roots
        self.incomingEdges = incomingEdges
        self.outgoingEdges = outgoingEdges
        self.sentence = sentence

if __name__ == "__main__":

    sentence = yaml.load (open("one.yaml", "r"))
    print (sentence.words)
