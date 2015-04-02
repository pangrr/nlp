import yaml


if __name__ == "__main__":


class Translator:
    def __init__ (self):
        # The ontology used by this translator.
        self.onto

        # A list of sentences to translate.
        self.sents = []


    # Translate all sentences.
    def batchTrans (self):
        for sent in self.sents:
            self.testFrame (sent)
            self.trans (sent)


    # Translate the given sentence using the given frame.
    # Used in self.batchTranslate ()
    def trans (self, sent, frame):
        sent.trans = "ONT::" + frame.sense
        for edge in sent.edges:
            if frame.args.has_key (edge[0]):
                sent.trans += " " + frame.args[edge[0]] + " " + edge[1] + "-" + edge[2]



    # Load sentences from file.
    def loadSent (self, file):
        f = open (file, "r")
        parsedSentList = yaml.safe_load (f)
        f.close ()

        for parsedSent in parsedSentList:
            self.sents.append (Sentence(parsedSent))






    # Compute and update the similarity between the given sentence and all the frames belongs to the root verb in the sentence.
    # Return the frame with the most similarity.
    def selectFrame (self, sent):
        # Compute and update similarity for each frame.
        for frame in self.onto.dict[sent.root]:
            frame.updateSim (sent)

        # Select the best frame.
        bestFrame = slef.onto.dict[sent.root][0]
        for frame in self.onto.dict[sent.root]:
            if fram.sim > bestFrame:
                bestFrame = frame

        return bestFrame











class Ontology:
    # Read and parse the given file to build the ontology.
    def __init__ (self, file):

        # A dictionary representing the ontology in the form of {word: frames} where frames is a list of frames of the word.
        # A frame is a dictionary of arguments in the form of {syntax: semantic}.
        self.dict = {}
        f = open (file, "r")
        onto = yaml.safe_load (f)
        f.close ()

        for sense in onto:
            word = sense["words"]
            if not self.dict.has_key (word):
                self.dict[word] = []

            frames = sense["frames"]
            for args in frames:
                frame = {"word": word, "sense": sense["ontoTypes"]}
                for arg in args["arguments"]:
                    frame[arg["syntax"]] = arg["semantic"]
                self.dict[word].append (frame)








class Frame:
    def __init__ (self):
        # A string representing the word that the frame belongs to.
        self.word

        # A string representing the name of the sense that the frame belongs to.
        self.sense

        # A dictionary representing the arguments of the frame in the form of {syntax: semantic}
        self.args


        # A float number representing the similarity between the frame and a certain sentence.
        # This similarity is updated for each sentence during translation.
        # This similarity is used for selecting the best frame for a certain sentence.
        self.sim = 0.0

    # Compute and return the similarity of the given sentence and the frame
    # by counting the matches between syntax in the arguments and label in the edges of the sentence.
    def updateSim (self, sent):
        for edge in sent.edges:
            if self.args.has_key (edge[0]):
                self.sim += 1.0
        self.sim /= len (sent.edges)









class Sentence:
    # Build a sentence object from a parseOutput in the file.
    def __init__ (self, parsedSent):

        # A dictionary representing each word in its root form and its index in the sentence in the form of {index: word}.
        self.lemma = {}
        for entry in parsedSent["lemma"]:
            lemma[entry["index"]] = entry["value"]

        # A string representing the root verb of the sentence.
        self.root = self.lemma[parsedSent["roots"][0]]

        # A list of tuples representing edges that points from other words to the root verb in the sentence.
        # The list is sorted in the order as the words appear in the sentence.
        # Each tuple represents an edge in the form of (label, word, position)
        self.edges = []
        for entry in parsedSent["incommingEdges"]:
            if lemma[entry["target"]] == self.root:
                self.edges.append ((entry["label"], lemma[entry["node"]]))

        # A string representing the original sentence.
        self.origin = parsedSent["sentence"]

        # A string representing the translation of the sentence.
        self.trans = ""

