from os.path import isfile, basename, abspath
import argparse
import sys

################################################################################
#                            Binary Tree Structure                             #
################################################################################
class Node:
    def __init__(self, character, code=-1):
        self.character =character
        self.code =code
        self.rChild =None
        self.lChild =None

class Tree:
    def __init__(self):
        self.root =None
        self.currentNode =None
        self.lastNode =None
        self.numWords =0
    
    def print_tree(self, node, prefix=""):
        if node is None:
            return
        prefix+=node.character
        if node.code != -1:
            print("{:9} {}".format(node.code, prefix))
        self.print_tree(node.rChild, prefix)
        self.print_tree(node.lChild, prefix[:-1])
    
    def set_word_number(self, node, lvl=0):
        if node is None:
            return
        if lvl == 0:
            self.numWords=0
        if node.code != -1:
            self.numWords +=1
        self.set_word_number(node.rChild, lvl+1)
        self.set_word_number(node.lChild, lvl+1)


################################################################################
#                                 Main Class                                   #
################################################################################
class Tokenizer:

    def __init__(self):
        self.fileObj =None      # variable to handle file/stdin
        self.curr_node =None    # current node in data structure (Tokenize)
        #----------------------------------------------------------------------#
        self.rChar =''          # calu
        self.wordCode =-1       # code_mot
        self.wordEnd =True      # fin_mot
        #----------------------------------------------------------------------#
        self.sep =' .,;:!?\'"`-+/\\\n\t_\0' # separators
        self.spaces =' \n\t\0'              # spacing characters
        self.tok =Tree()        # tokenizer data structure


    def print_vocab(self):
        self.tok.print_tree(self.tok.root)

    def process_input(self, process, filePath=None):
        if filePath is None:        # read from STDIN by default
            self.fileObj =sys.stdin
        else:                       # or from file, if a valid path is specified
            if not isfile(filePath):
                print("[ERREUR] le fichier \""+filePath+"\" n'existe pas.")
                exit(4)
            self.fileObj =open(filePath, 'r')
        process()                   
        if filePath is not None:    
            self.fileObj.close()
        self.fileObj =None
    
    #==========================================================================#
    #====================== Binary Tree Construction ==========================#
    def read_char(self):
        self.wordEnd=True
        self.wordCode =-1
        self.rChar=''
        line ="\n"
        while self.fileObj is not None and line != "":
            line=self.fileObj.readline()
            tmp =line.rstrip().split(' ')
            if len(tmp) == 1 and tmp[0] == "":
                continue    # empty line
            if len(tmp) != 2:
                print(  "[ERREUR] format du fichier de lexique incorrect!\n"
                        +"Ligne: \""+line+"\"")
                exit(3)
            if tmp[0].isdigit() == False:
                print("[ERREUR] code "+tmp[0]+" is not a digit!\nWord="+tmp[1])
                exit(2)
            self.wordEnd =False
            self.wordCode =int(tmp[0])
            for i in range(len(tmp[1])):
                self.rChar =tmp[1][i]
                if i == len(tmp[1])-1:
                    self.wordEnd =True
                yield True
        yield False
        
    # lire_lexique()
    def read_lexicon(self):
        # Attention: On boucle de façon un peu spéciale (sur un générateur dont
        # la valeur de retour nous dit s'il faut sortir), mais c'est pour coller
        # avec la méthode vue en TD
        for t in self.read_char():
            if not t:   # prevent loop on empty files
                break
            
            if self.tok.root is None:   # Init case (very first char)
                r =self.tok.root =Node(self.rChar)
                p =None
                if self.wordEnd:        # Maybe the first char is terminal?
                    r.code =self.wordCode
                    p =self.tok.root
                continue

            elif p is None:             # new branch to the right (next char)
                p =Node(self.rChar)
                r.rChild =p
            else:                       # new branch to the left (alt. char)
                # keep looking for this alternative character
                while p is not None and p.character != self.rChar: 
                    r =p
                    p =p.lChild
                # create new alternate character if we didn't found it
                if p is None:
                    p =Node(self.rChar)
                    r.lChild =p
            
            # Check for next move...
            if self.wordEnd:            # If it's the last character
                p.code =self.wordCode   # set the code
                p =self.tok.root        # and go back to the root for next word
            else:           # if there's another character following,
                r =p        # the "current" node become the futur "parent"
                p =p.rChild # and we keep going to the right; current=rightChild

    def load_lexicon(self, filePath=None):
        self.process_input(self.read_lexicon, filePath)

    #==========================================================================#
    #============================= Tokenizer ==================================#
    def get_txt(self):
        line ="\n"
        while self.fileObj is not None and line != "":
            line =self.fileObj.readline()
            yield line

    def tokenize(self, line, i):
        self.wordCode=-1
        imot=i
        self.curr_node =self.tok.root   # this can cut the analysis if end of 
                                        # line is reached before last character
                                        # (when the word is cut in two)
        while i < len(line) and self.curr_node is not None:
            if (line[i]==self.curr_node.character or
            (line[i]==' ' and self.curr_node.character=='_')):  # composed word
                if (    self.curr_node.code!=-1 and 
                        (((len(line)>i+1 and line[i+1] in self.sep) or
                        len(line)==i+1) or line[i] in self.sep)
                ):
                    self.wordCode=self.curr_node.code
                    imot=i
                self.curr_node=self.curr_node.rChild
                i+=1
            else:
                self.curr_node=self.curr_node.lChild
        return imot

    def txt2code(self):
        for l in self.get_txt():
            i =0
            while i < len(l):
                if (l[i] not in self.spaces):   # escape all spacing characters
                    i=self.tokenize(l,i)
                    if (self.wordCode != -1):
                        print(str(self.wordCode)+" ", end='')
                    else:   # unknown word, print code '0' and get to next word
                        print("0 ", end='')
                        j =i
                        while i<len(l) and l[i] not in self.sep:
                            i +=1
                        if i>j:
                            i-=1    # keep going to next valid character
                elif l[i]=="\n":
                    print()
                i +=1

    def process_tok(self, filePath):
        self.process_input(self.txt2code, filePath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-lex", help="Path to a lexicon file.",
                        default=None)
    parser.add_argument("-txt", help="Path to a text file.",
                        default=None)
    parser.add_argument("--verbose", "--v", help="If outputs are needed.",
                        action="store_true")
    args = parser.parse_args()
    if args.lex is None and args.txt is None:
        print("[ERROR] Can't read both inputs at the same time in stdin")
        exit(1)

    tokenizer =Tokenizer()
    if args.verbose:
        print("Chargement du vocabulaire...")
    tokenizer.load_lexicon(args.lex)
    if args.verbose:
        print("VOCAB:")
        tokenizer.print_vocab()
    tokenizer.process_tok(args.txt)