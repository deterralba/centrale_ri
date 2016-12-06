import time
import argparse

from collections import namedtuple, defaultdict

import tools.cacm as cacm
import tools.search as se
import tools.token as tk

def get_all_tokens(docs, common_words, print_res=False):
    tokens = [t for doc in docs for t in cacm.tokenize_doc(doc, remove_common=False, lemm=True)]
    print('Number of tokens (after lower/ ponctuation and basic duplicate removal): {}'.format(len(tokens)))
    tokens = list(set(tokens))
    print('Number of tokens (after removing duplicates): {}'.format(len(tokens)))
    tokens = [t for t in tokens if t not in common_words]
    print('Number of tokens (after removing {} common words): {}'.format(len(common_words), len(tokens)))
    if print_res:
        input('Type something to see the tokens')
        print(tokens)
    return tokens

def add_doc_to_binary_index(index_dict, doc, common_words):
    for t in cacm.tokenize_doc(doc, common_words, remove_common=True, lemm=True):
        index_dict[t] |= {doc.id}

def build_binary_index(all_docs_dict, common_words):
    index = defaultdict(set)
    for doc in all_docs_dict.values():
        add_doc_to_binary_index(index, doc, common_words)
    return index

def add_doc_to_vector_index(index_dict, doc, common_words):
    for t, freq in cacm.tokenize_doc_with_freq(doc, common_words):
        index_dict[t] |= {(doc.id, freq)}

def build_vector_index(all_docs_dict, common_words):
    index = defaultdict(set)
    for doc in all_docs_dict.values():
        add_doc_to_vector_index(index, doc, common_words)
    return index

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('type')
    args = parser.parse_args()
    if args.type not in ['bin', 'vec']:
        raise ValueError('Invalid type {}!'.format(args.type))

    start_time = time.time()
    print('Parsing cacm.all')
    all_docs_dict = cacm.parse_document()
    print('Parsing common_words')
    common_words = cacm.parse_common_words()

    '''
    print(cacm.tokenize_doc_with_freq(all_docs[-1], common_words))
    print(cacm.tokenize_doc(all_docs[-1], common_words, True, True))
    '''

    #print(vector_index)
    #print(vector_index['program'])

    print('Building binary index')
    binary_index = build_binary_index(all_docs_dict, common_words)
    vector_index = None
    if args.type == 'vec':
        print('Building vector index')
        vector_index = build_vector_index(all_docs_dict, common_words)
    print('Done! It took {:.2f}s to do everything.'.format(time.time() - start_time))
    try:
        while True:
            se.search(args.type, all_docs_dict, common_words, binary_index, vector_index)
    except (KeyboardInterrupt, EOFError):
        print('\nExiting')



    '''
    docs1 = docs[:len(docs)//2]
    docs2 = docs[len(docs)//2:]
    get_all_tokens(docs1, common_words)#, print_res=True)
    get_all_tokens(docs2, common_words)
    '''
    # all_tokens = get_all_tokens(all_docs, common_words)




