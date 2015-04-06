from __future__ import print_function
import yaml


class Translator:
    def __init__ (self, sentFile, ontoFile):
        # The ontology used by this translator.
        self.onto = Ontology (ontoFile)

        # A list of sentences to translate.
        self.sents = self.loadSent (sentFile)

        # A dictionary in the form of {sentence edge label: ontology frame argument syntax}.
        self.labelSyntax = {"nsubj": "lsubj", "dobj": "lobj", "prep_from": "lcomp", "prep_to": "lcomp", "prep_into": "lcomp", "xcomp": "lcomp"}


    # Translate all sentences.
    def batchTrans (self):
        for sent in self.sents:
            # Find the best frame.
            frame = self.selectFrame (sent)
            # Translate the sentence by this frame.
            self.trans (sent, frame)


    # Translate the given sentence using the given frame.
    # Used in self.batchTranslate ()
    def trans (self, sent, frame):
        sent.trans = "ONT::" + frame.ontotype
        for edge in sent.edges:
            label = edge[0]
            word = edge[1]
            wordIndex = edge[2]

            if label in self.labelSyntax:
                syntax = self.labelSyntax[label]
                if syntax in frame.args:
                    semantic = frame.args[syntax]["semantic"]
                    sent.trans += " " + semantic + " " + word + "-" + wordIndex



    # Load sentences from file.
    def loadSent (self, file):
        f = open (file, "r")
        parsedSentList = yaml.safe_load (f)
        f.close ()

        sents = []
        for parsedSent in parsedSentList:
            sents.append (Sentence(parsedSent))
        return sents






    # Compute and update the similarity between the given sentence and all the frames belongs to the root verb in the sentence.
    # Return the frame with the most similarity.
    def selectFrame (self, sent):
        candFrame = self.onto.wordFrame[sent.root]
        # Compute and update similarity for each frame.
        for frame in candFrame:
            frame.updateSim (sent, self.labelSyntax)

        # Select the best frame.
        bestFrame = candFrame[0]
        for frame in candFrame:
            if frame.sim > bestFrame.sim:
                bestFrame = frame

        return bestFrame


    # Save all translations to file.
    def writeRes (self, file):
        f = open (file, "w")
        for sent in self.sents:
            f.write ("\n" + sent.origin + "\n")
            f.write (sent.trans + "\n")
        f.close ()








class Ontology:
    # Read and parse the given file to build the ontology.
    def __init__ (self, file):

        # A dictionary representing the ontology in the form of {word: frames} where frames is a list of frames of the word.
        self.wordFrame = {}

        f = open (file, "r")
        onto = yaml.safe_load (f)
        f.close ()

        for sense in onto:
            word = sense["words"]
            ontotype = sense["ontotypes"]

            if not (word in self.wordFrame):
                self.wordFrame[word] = []

            frames = sense["frames"]
            for _args in frames: # Arguments is a frame.
                args = {}
                for arg in _args["arguments"]:   # An argument is an element in the frame.
                    key = arg["syntax"]
                    value = {"semantic": arg["semantic"], "constituent": arg["constituent"], "restrictions": arg["restrictions"]}
                    args[key] = value


                frame = Frame (word, ontotype, args)
                self.wordFrame[word].append (frame)








class Frame:
    def __init__ (self, word, ontotype, args):
        # A string representing the word that the frame belongs to.
        self.word = word

        # A string representing the name of the ontology type that the frame belongs to.
        self.ontotype = ontotype

        # A dictionary representing the arguments of the frame in the form of {syntax: semantic}
        self.args = args


        # A float number representing the similarity between the frame and a certain sentence.
        # This similarity is updated for each sentence during translation.
        # This similarity is used for selecting the best frame for a certain sentence.
        self.sim = 0.0

    # Compute and update the similarity of the given sentence and the frame
    # by counting the matches between syntax in the arguments and label in the edges of the sentence.
    def updateSim (self, sent, labelSyntax):
        self.sim = 0.0

        for edge in sent.edges:
            label = edge[0]
            if label in labelSyntax:
                syntax = labelSyntax[label]
                if syntax in self.args:
                    value = self.args[syntax]
                    constituent = value["constituent"]
                    semantic = value["semantic"]
                    if "prep" in label:
                        if constituent == "pp":
                            if ("from" in label and semantic == "source") or (("to" in label or "into" in label) and semantic == "result"):
                                self.sim += 1.0
                    else:
                        self.sim += 1.0

        self.sim /= len (self.args)









class Sentence:
    # Build a sentence object from a parseOutput in the file.
    def __init__ (self, parsedSent):

        # A dictionary representing each word in its root form and its index in the sentence in the form of {index: word}.
        self.lemma = {}
        for entry in parsedSent["lemma"]:
            self.lemma[entry["index"]] = entry["value"]

        # A string representing the root verb of the sentence.
        self.root = self.lemma[parsedSent["roots"][0]]

        # A list of tuples representing edges that points from other words to the root verb in the sentence.
        # The list is sorted in the order as the words appear in the sentence.
        # Each tuple represents an edge in the form of (label, word, index)
        self.edges = []
        for entry in parsedSent["incommingEdges"]:
            targetWord = self.lemma[entry["target"]]
            if targetWord == self.root:
                label = entry["label"]
                index = entry["node"]
                word = self.lemma[index]
                self.edges.append ((label, word, index))

        # A string representing the original sentence.
        self.origin = parsedSent["sentence"]

        # A string representing the translation of the sentence.
        self.trans = ""







if __name__ == "__main__":
    translator = Translator ("input-parsed.yaml", "lexicon.yaml")
    translator.batchTrans ()
    translator.writeRes ("result")
    print ("Translation complete. Please check file 'result'.")
