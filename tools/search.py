import time
import math
from functools import reduce
from collections import defaultdict
import tools.token as tk
import tools.cacm as cacm

## Parameter
SHOW_N_FIRST = 10  # number of results to show in the command line prompt

#VECTOR_SEARCH = 'custom-tf' # first home made tfidf, see function custom_normalize
VECTOR_SEARCH = 'tfidf'

def search(index_type, all_docs_dict, common_words, binary_index=None, vector_index=None, vector_docs_meta=None):
    print('Type your query (union is shown if several words are typed)')
    q = input('> ')
    start_time = time.time()
    if q.startswith('#'):
        reverse_search(all_docs_dict, common_words, q[1:])
    else:
        tokens = tk.filter_tokens(tk.extract_tokens(q), common_words, remove_common=True, lemm=True)
        if not tokens:
            print('Only common words or ponctuations were given. Try again.')
        else:
            print('Terms searched: ', *tokens)
            if index_type == 'bin':
                res = binary_search(tokens, binary_index)
            elif index_type == 'vec':
                res = vector_search(tokens, vector_index, vector_docs_meta)
            if res:
                res = format_res(index_type, all_docs_dict, res)
                print('{} documents found (type #id to see document details):'.format(len(res)))
                if len(res) > SHOW_N_FIRST:
                    print('Only the best {} results are shown'.format(SHOW_N_FIRST))
                print(*res[:SHOW_N_FIRST], sep=', ')
            else:
                print('No results were found')
    print('\nSearching took {:.2f}ms.'.format((time.time() - start_time)*1000))
    print('+'*30, '\n')

def reverse_search(all_docs_dict, common_words, q):
    try:
        id = int(q.strip())
        doc = all_docs_dict[id]
        print('Document found: ', doc)
        print('Tokens extracted:\n ', cacm.tokenize_doc(doc, common_words, remove_common=True, lemm=True))
    except StopIteration:
        print('No doc with id ', id)
    except (IOError, ValueError):
        print('# must be followed by a number')

def binary_search(tokens, binary_index):
    docs_ids = [binary_index[t] for t in tokens]
    relevant_ids = reduce(lambda x, y: x|y, docs_ids)  # |: union    &: intersection
    return sorted(relevant_ids)

def filter_tuple_list_with_ids(tuple_list, ids):
    '''[(1,),(2,),(3,),(4,)], {1,2} -> [(1,),(2,)]'''
    return list(filter(lambda x: x[0] in ids, tuple_list))

def reverse_order_dict_by_value(input_dict):
    return sorted(input_dict.items(), key=lambda x: x[1], reverse=True)

def custom_normalize(couples_id_card):
    if not couples_id_card:
        return []
    couples = []
    card_max = max(card for id_, card in couples_id_card)
    for id_, card in couples_id_card:
        couples.append((id_, math.log(1 + card/card_max)))
    return couples

def normalize_term_in_document(couples_id_card, vector_docs_meta):
    if not couples_id_card:
        return []
    couples = []

    for id_, card in couples_id_card:
        card_doc = vector_docs_meta[id_]  # number of terms in document

        #couples.append((id_, math.log(1 + card/card_doc)))
        couples.append((id_, card/card_doc))
        #couples.append((id_, card))
    return couples

def normalize_term_in_collection(couples_id_card, nb_of_doc_in_collection):
    if not couples_id_card:
        return []
    couples = []
    nb_of_doc_with_token = len(couples_id_card)

    #idf = math.log(nb_of_doc_in_collection/nb_of_doc_with_token)
    idf = math.log(nb_of_doc_in_collection/(1 + nb_of_doc_with_token))
    #idf = 1

    for id_, card in couples_id_card:
        couples.append((id_, card*idf))
    return couples

def reduce_couples_by_token(couples_by_token):
    res_dict = defaultdict(lambda: 0)
    for couples_for_one_token in couples_by_token:
        for doc_id, weight in couples_for_one_token:
            res_dict[doc_id] += weight
    return reverse_order_dict_by_value(res_dict)

def vector_search(tokens, vector_index, vector_docs_meta):
    nb_of_doc_in_collection = len(vector_docs_meta)
    list_of_couples_by_token = []
    for t in tokens:
        #print('token', t)
        couples_id_card = vector_index[t]
        if VECTOR_SEARCH == 'tfidf':
            couples_id_tf = normalize_term_in_document(couples_id_card, vector_docs_meta)
            couples_id_tfidf = normalize_term_in_collection(couples_id_tf, nb_of_doc_in_collection)
        elif VECTOR_SEARCH == 'custom-tf':
            couples_id_tfidf = custom_normalize(couples_id_card)
        else:
            raise ValueError('Invalid VECTOR_SEARCH value {}'.format(VECTOR_SEARCH))
        list_of_couples_by_token.append(couples_id_tfidf)

    results = reduce_couples_by_token(list_of_couples_by_token)
    return results

def get_doc_title(all_docs_dict, doc_id):
    return all_docs_dict[doc_id].title

def format_res(index_type, all_docs_dict, results):
    if index_type == 'bin':
        res = ['\nId:{}: {}'.format(res, get_doc_title(all_docs_dict, res))
               for res in results]
        return res
    elif index_type == 'vec':
        res = ['\nId:{} (score: {:0.2f}): {}'.format(res[0], res[1], get_doc_title(all_docs_dict, res[0]))
               for res in results]
        return res
