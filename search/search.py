import sys, os

def read_file(testfile):
    with open(testfile, 'r') as file:
        queries = file.readlines()
    return queries


def write_file(outputs, path_to_output):
    '''outputs should be a list of lists.
        len(outputs) = number of queries
        Each element in outputs should be a list of titles corresponding to a particular query.'''
    with open(path_to_output, 'w') as file:
        for output in outputs:
            for line in output:
                file.write(line.strip() + '\n')
            file.write('\n')

def search(path_to_index, queries):
    a = os.path.join (path_to_index, 'inverted_index')
    from stemmer import stemmer
    from stopwords import stopwords
    from search_handler import search
    stemmer = stemmer()
    stopwords = stopwords()
    search = search (a, stemmer, stopwords)
    outputs = []
    for query in queries:
        the_result = search.search (query)
        if the_result is None:
            outputs.append (['.'] * 10)
        else:
            outputs.append (the_result)
    return outputs

def main():
    path_to_index = sys.argv[1]
    testfile = sys.argv[2]
    path_to_output = sys.argv[3]

    queries = read_file(testfile)
    outputs = search(path_to_index, queries)
    # print (outputs)
    write_file(outputs, path_to_output)


if __name__ == '__main__':
    main()
