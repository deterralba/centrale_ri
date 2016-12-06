import time
import math
from functools import reduce
from collections import defaultdict
import tools.token as tk
import tools.cacm as cacm

def search(index_type, all_docs_dict, common_words, binary_index, vector_index=None):
    print('Type your query (intersection is shown if several words are typed)')
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
                res = vector_search(tokens, binary_index, vector_index)
            if res:
                res = format_res(index_type, all_docs_dict, res)
                print('{} documents found (type #id to see document details):'.format(len(res)))
                print(*res, sep=', ')
            else:
                print('No results were found')
    print('Searching took {:.2f}ms.'.format((time.time() - start_time)*1000))

def reverse_search(all_docs_dict, common_words, q):
    try:
        id = int(q.strip())
        doc = all_docs_dict[id]
        print('Document found: ', doc)
        print('Tokens extracted:\n ', cacm.tokenize_doc(doc, common_words, remove_common=True, lemm=True))
    except StopIteration:
        print('No doc with id ', id)
    except (IOError, ValueError):
        print('! must be followed by a number')

def binary_search(tokens, binary_index):
    docs_ids = [binary_index[t] for t in tokens]
    relevant_ids = reduce(lambda x, y: x&y, docs_ids)
    return sorted(relevant_ids)

def filter_tuple_list_with_ids(tuple_list, ids):
    '''[(1,),(2,),(3,),(4,)], {1,2} -> [(1,),(2,)]'''
    return list(filter(lambda x: x[0] in ids, tuple_list))

def reverse_order_dict_by_value(input_dict):
    return sorted(input_dict.items(), key=lambda x: x[1], reverse=True)

def normalize_index_couples(index_items):
    if not index_items:
        return []
    couples = []
    maxi = max(couple[1] for couple in index_items)
    for couple in index_items:
        couples.append((couple[0], math.log(1+couple[1]/maxi)))
    return couples

def reduce_couples_by_token(couples_by_token):
    res_dict = defaultdict(lambda: 0)
    for couples_for_one_token in couples_by_token:
        for doc_id, weight in couples_for_one_token:
            res_dict[doc_id] += weight
    return reverse_order_dict_by_value(res_dict)

def vector_search(tokens, binary_index, vector_index):
    relevant_ids = binary_search(tokens, binary_index)

    list_of_couples_by_token = []
    for t in tokens:
        couples_id_freq = filter_tuple_list_with_ids(vector_index[t], relevant_ids)
        couples_id_weight = normalize_index_couples(couples_id_freq)
        list_of_couples_by_token.append(couples_id_weight)

    results = reduce_couples_by_token(list_of_couples_by_token)
    return results

def get_doc_title(all_docs_dict, doc_id):
    return all_docs_dict[doc_id].title

def format_res(index_type, all_docs_dict, results):
    if index_type == 'bin':
        res = ['\nId:{}: {}'.format(res[0], res[1], get_doc_title(all_docs_dict, res[0]))
               for res in results]
        return res
    elif index_type == 'vec':
        res = ['\nId:{} (score: {:0.2f}): {}'.format(res[0], res[1], get_doc_title(all_docs_dict, res[0]))
               for res in results]
        return res
