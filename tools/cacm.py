import re
from statistics import mean, stdev
from collections import namedtuple, defaultdict

import tools.token as tk

docTuple = namedtuple('docTuple', 'id, title, summary, keywords')

def _get_line(f):
    l = f.readline()
    l = l.replace('\n', ' ')
    return l

def parse_common_words():
    with open('data/cacm/common_words') as f:
        common_words = set(l.replace('\n', '') for l in f)
    return common_words

def _parse_queries():
    queries = dict()
    with open('data/cacm/query.text') as f:
        query, next_id = _parse_one_doc(f)
        while next_id is not None:
            query, next_id = _parse_one_doc(f, next_id)
            queries[query.id] = query.summary
    return queries

def _parse_relevant_docs():
    relevant_docs = defaultdict(list)
    with open('data/cacm/qrels.text') as f:
        for l in f:
            query_id, doc_id, _, _ = l.split()
            relevant_docs[int(query_id)].append(int(doc_id))
    return relevant_docs

def parse_document():
    docs_dict = dict()
    with open('data/cacm/cacm.all') as f:
        doc, next_id = _parse_one_doc(f)
        while next_id is not None:
            doc, next_id = _parse_one_doc(f, next_id)
            docs_dict[doc.id] = doc
    return docs_dict

def _is_doc_end_line(l):
    return l.startswith('.I') or l == ''

def _parse_one_doc(f, id=1):
    ''' Parses cacm.all and query.text '''
    l = _get_line(f)
    part = ''
    keywords = ''
    summary = ''
    title = ''
    while not _is_doc_end_line(l):
        if l.startswith('.T'):
            part = 'title'
        elif l.startswith('.W'):
            part = 'summary'
        elif l.startswith('.K'):
            part = 'keywords'
        elif l.startswith('.'):
            part = 'other'
        else:
            if part == 'other':
                pass
            elif part == 'summary':
                summary += l
            elif part == 'keywords':
                keywords += l
            elif part == 'title':
                title += l
            else:
                raise ValueError('WTF is going on')
        l = _get_line(f)

    title = title.strip()
    keywords = keywords.strip()
    summary = summary.strip()
    doc = docTuple(id, title, summary, keywords)

    if l.startswith('.I'):
        next_id = int(re.findall(r'\d+', l)[-1])
        # print('id:{} - END OF DOC - next id: {}'.format(id, next_id))
    elif l == '':
        next_id = None
        # print('END OF FILE')
    else:
        raise ValueError('We should not be here')
    return (doc, next_id)

def tokenize_doc(doc, common_words, remove_common, lemm):
    tokens = {
        t for field in doc[1:]
            for t in tk.filter_tokens(tk.extract_tokens(field), common_words, remove_common, lemm)
    }
    return tokens

def tokenize_doc_with_card(doc, common_words):
    couples_dict = defaultdict(lambda: [0, 0])
    for field in doc[1:]:
        tokens_and_card = tk.filter_tokens_with_card(tk.extract_tokens(field), common_words)
        for t, card in tokens_and_card:
            couples_dict[t] = [t, couples_dict[t][1] + card]
    couples = set(tuple(couple) for couple in couples_dict.values())
    return couples

def evaluate(index_type, common_words, vector_index, vector_docs_meta, show=None, RANK_K=None, CALC_MAP=None):
    from .search import vector_search
    from .measure import get_recall, get_precision, F1_measure, MAP
    from time import time
    relevant_docs = _parse_relevant_docs()
    results_for_query = {}
    queries = _parse_queries()
    rec_pre = []
    F1 = []
    search_time = []
    for query_id, query in queries.items():
        start_time = time()
        truth = relevant_docs[query_id]
        tokens = tk.filter_tokens(
            tk.extract_tokens(query),
            common_words, remove_common=True, lemm=True
        )
        results = [res[0] for res in vector_search(tokens, vector_index, vector_docs_meta)]

        end_time = time() - start_time
        search_time.append(end_time*1000)

        results_for_query[query_id] = results
        results_at_k = results[:RANK_K]
        precision = get_precision(truth, results_at_k)
        recall = get_recall(truth, results_at_k)
        rec_pre.append((recall, precision))
        F1.append(F1_measure(recall, precision))

    print('Average F1 mesure (at rank {}): {:0.3f} (std deviation: {:0.2f})'.format(RANK_K, mean(F1), stdev(F1)))
    print('Average search time: {:0.3f}ms (std deviation: {:0.2f})'.format(mean(search_time), stdev(search_time)))

    if CALC_MAP:
        map_ = MAP(queries, relevant_docs, results_for_query)
        print('Mean Average Precision: {:0.3f}'.format(map_))

    if show:
        from .measure import show_recall_precision
        show_recall_precision(rec_pre, RANK_K)

