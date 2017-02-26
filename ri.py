import time
import argparse
from collections import namedtuple, defaultdict

import tools.search as se
import tools.token as tk


## Binary index
def build_binary_index(all_docs_dict, common_words):
    index = defaultdict(set)
    for doc in all_docs_dict.values():
        add_doc_to_binary_index(index, doc, common_words)
    return index

def add_doc_to_binary_index(index_dict, doc, common_words):
    for t in collection.tokenize_doc(doc, common_words, remove_common=True, lemm=True):
        index_dict[t] |= {doc.id}

## Vector index
def build_vector_index(all_docs_dict, common_words):
    index = defaultdict(set)
    for doc in all_docs_dict.values():
        add_doc_to_vector_index(index, doc, common_words)
    return index

def add_doc_to_vector_index(index_dict, doc, common_words):
    for t, freq in collection.tokenize_doc_with_freq(doc, common_words):
        index_dict[t] |= {(doc.id, freq)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', choices=['cs276', 'cacm'])
    parser.add_argument('type', choices=['bin', 'vec'])
    parser.add_argument('--evaluate', help='test the results of the index (only for cacm)', action='store_true')
    args = parser.parse_args()

    start_time = time.time()

    '''
        The collection imported must provide several functions:
            - parse_document that returns a dict of documents by id
            - parse_common_words that returns a list of common_words
            - tokenize_doc, used for the binary index
            - tokenize_doc_with_freq, used for the vector index
    '''
    if args.source == 'cacm':
        import tools.cacm as collection
    elif args.source == 'cs276':
        import tools.cs as collection

    print('Parsing {}'.format(args.source))
    all_docs_dict = collection.parse_document()
    print('Parsing common_words')
    common_words = collection.parse_common_words()

    print('Building binary index')
    binary_index = build_binary_index(all_docs_dict, common_words)
    vector_index = None
    if args.type == 'vec':
        print('Building vector index')
        vector_index = build_vector_index(all_docs_dict, common_words)
    print('Done! It took {:.2f}s to do everything.'.format(time.time() - start_time))

    if args.evaluate:  # evaluates the searches results for cacm
        if args.source != 'cacm' or args.type != 'vec':
            print('Evaluation is only possible with cacm and vector index, exiting')
        else:
            collection.evaluate(args.type, common_words, binary_index, vector_index)
    else:  # starts the search prompt
        try:
            while True:
                se.search(args.type, all_docs_dict, common_words, binary_index, vector_index)
        except (KeyboardInterrupt, EOFError):
            print('\nExiting')



    '''
    print(cacm.tokenize_doc_with_freq(all_docs[-1], common_words))
    print(cacm.tokenize_doc(all_docs[-1], common_words, True, True))
    '''
    '''
    docs1 = docs[:len(docs)//2]
    docs2 = docs[len(docs)//2:]
    tk.get_all_tokens(docs1, common_words)#, print_res=True)
    tk.get_all_tokens(docs2, common_words)
    '''
    # all_tokens = tk.get_all_tokens(all_docs, common_words)




