from string import whitespace
from os.path import isfile
from math import log
import argparse
import sys

################################################################################
#                             Ngram Data Structure                             #
################################################################################
class SuperGram:
    def __init__(self):
        self.ngrams ={} # Dict of Dict for occ (1st key = 'N' gram, 2nd = token)
        self.vocabSize ={} # size of each Ngram vocabulary
    
    def add_token(self, N, gram):
        if N not in self.ngrams:
            self.ngrams[N] ={}
            self.vocabSize[N] =0
        if gram in self.ngrams[N]:
            self.ngrams[N][gram] +=1
        else:
            self.ngrams[N][gram] =1
            self.vocabSize[N] +=1
    
    def nbVocab(self, N):
        if N in self.vocabSize:
            return self.vocabSize[N]
        return 0
    
    def nbGram(self, N, gram):
        if N in self.ngrams:
            if gram in self.ngrams[N]:
                return self.ngrams[N][gram]
        return 0
    
    def print(self):
        # Note: _ We assume that 'N' keys must be integers here.
        #       _ We assume 'k' keys are strings
        #       otherwise this method will fail
        for N in self.ngrams:
            print(str(N)+"-gram:")
            for k in self.ngrams[N]:
                print(k.replace('_', ' ')+" "+str(self.ngrams[N][k]))
    

################################################################################
#                                 Main Class                                   #
################################################################################
class LangageModel:
    def __init__(self, alpha=0.01):
        self.fileObj =None          # variable to handle file/stdin
        #----------------------------------------------------------------------#
        self.spGram =SuperGram()    # Ngrams
        self.a =alpha               # representation of unknown words (in %)
    
    def print_vocab(self):
        self.spGram.print()

    def nb(self, N, gram):
        return self.spGram.nbGram(N, gram)
    
    def vocabSize(self, N):
        vocSize =self.spGram.nbVocab(N)
        return (float)(vocSize+vocSize*self.a)

    def process_input(self, process, filePath=None):
        if filePath is None:        # read from STDIN by default
            self.fileObj =sys.stdin
        else:                       # or from file, if a valid path is specified
            if not isfile(filePath):
                print("[ERREUR] le fichier \""+filePath+"\" n'existe pas.")
                exit(3)
            self.fileObj =open(filePath, 'r')
        process()                   # process the method
        if filePath is not None:    # close file if needed
            self.fileObj.close()
        self.fileObj =None

    def get_text(self):
        line ="\n"
        while self.fileObj is not None and line != "":
            line =self.fileObj.readline()
            yield line
    
    #==========================================================================#
    #=============================== Count ====================================#
    def ngrams_from_input(self, N_max=2):
        for line in self.get_text():
            prev =['<']                     # at each new line we clear history
                                            # also, we start with "<" character
            for e in line.rstrip('\n').split(" "):
                if e not in whitespace:
                    self.spGram.add_token(1, e) # count unigram
                    prev.append(e)
                    for n in range(1,N_max+1):  # generic way to count Ngrams
                        if len(prev) > n:
                            self.spGram.add_token(n+1, '_'.join(prev[:n+1]))
                    while len(prev) >= N_max:   # delete out of Ngram scope elem
                        prev =prev[1:]

    def get_vocab(self, filePath=None):
        self.process_input(self.ngrams_from_input, filePath)


    #==========================================================================#
    #============================ Perplexite ==================================#
    def logprob_Ngram(self, grams):
        N =len(grams)
        g ='_'.join(grams)
        n =self.spGram.nbVocab(1)+self.spGram.nbVocab(N)*self.a
        return -log((float)(self.nb(N, g)+self.a)/n)

    def logprob_1gram(self, gram):
        return -log((float)(self.nb(1, gram)+self.a)/self.vocabSize(1))

    def perplexite(self, N_max):
        for line in self.get_text():
            lp =0
            nb =0
            prev =['<']                     # at each new line we clear history
                                            # also, we start with "<" character
            for e in line.rstrip('\n').split(" "):
                if e not in whitespace:
                    if N_max == 1:          # unigram case
                        lp +=self.logprob_1gram(e)
                        continue
                    prev.append(e)          # Ngrams case
                    if len(prev) == N_max:
                        lp +=self.logprob_Ngram(prev)
                        prev =prev[1:]      # remove oldest word in sequence
                    nb +=1
            if nb > 0:				
                print(str(lp/nb)+" "+line)

    def eval_txt(self, N=2, filePath=None):
        if filePath is None:        # read from STDIN by default
            self.fileObj =sys.stdin
        else:                       # or from file, if a valid path is specified
            if not isfile(filePath):
                print("[ERREUR] le fichier \""+filePath+"\" n'existe pas.")
                exit(3)
            self.fileObj =open(filePath, 'r')
        self.perplexite(N)          # calcul perplexity
        if filePath is not None:    # close file if needed
            self.fileObj.close()
        self.fileObj =None





if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-count", "-c", help="Input file for Ngrams path.",
                        default=None)
    parser.add_argument("-eval", "-e", help="Input file with text to eval.",
                        default=None)
    parser.add_argument("-Ngram", "-N", "-n", help="'N' for Ngram",
                        default='2')
    parser.add_argument("--verbose", "--v", help="If outputs are needed.",
                        action="store_true")
    args = parser.parse_args()
    if args.count is None and args.eval is None:
        print("[ERROR] Can't read both inputs at the same time in stdin")
        exit(1)

    lm =LangageModel()
    if args.verbose:
        print("Read input...")
    lm.get_vocab(args.count)
    if args.verbose:
        print("COUNTED:")
        lm.print_vocab()
    lm.eval_txt(int(args.Ngram), args.eval)
