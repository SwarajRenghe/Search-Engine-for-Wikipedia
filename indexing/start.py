import pickle, os, sys
import time
start = time.time()

from stemmer import stemmer
from stopwords import stopwords
from parser import parser

stemmer = stemmer()
stopwords = stopwords()

path_to_dump = sys.argv[1]
path_to_index_folder = sys.argv[2]

print (path_to_index_folder)

wikipedia_parser = parser (path_to_index_folder, stemmer, stopwords)

wikipedia_parser.parse (path_to_dump)
wikipedia_parser.make_alphabet_pairs ()
# wikipedia_parser.merge_files ()
# wikipedia_parser.divide_files ()
end = time.time()
print ("It took", end-start, "seconds")