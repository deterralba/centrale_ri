import re
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

def tokenize_doc_with_freq(doc, common_words):
    couples_dict = defaultdict(lambda: [0, 0])
    for field in doc[1:]:
        tokens_and_freq = tk.filter_tokens_with_freq(tk.extract_tokens(field), common_words)
        for t, freq in tokens_and_freq:
            couples_dict[t] = [t, couples_dict[t][1] + freq]
    couples = set(tuple(couple) for couple in couples_dict.values())
    return couples

def evaluate(index_type, common_words, binary_index, vector_index):
    relevant_docs = _parse_relevant_docs()
    queries = _parse_queries()
    from .search import vector_search
    rec_pre = []
    for query_id, truth in relevant_docs.items():
        if len(truth) == 0:  # queries without relevant documents are filtered out
            continue
        else:
            query = queries[query_id]
            tokens = tk.filter_tokens(
                tk.extract_tokens(query),
                common_words, remove_common=True, lemm=True
            )
            results = [res[0] for res in vector_search(tokens, binary_index, vector_index)]
            rec_pre.append(
                (recall(truth, results), precision(truth, results))
            )
    rec_pre.sort(key=lambda x: x[0])  # sort (recall, precision) couples by recall
    print(rec_pre)
    show_recall_precision(rec_pre)

def show_recall_precision(rec_pre):
    from matplotlib import pyplot as plt
    import numpy as np
    recall = [x[0] for x in rec_pre]
    precision = [x[1] for x in rec_pre]
    decreasing_max_precision = np.maximum.accumulate(precision[::-1])[::-1]
    fig, ax = plt.subplots(1, 1)
    ax.plot(recall, precision, '--b')
    ax.step(recall, decreasing_max_precision, '-r')
    fig.show()
    input()

def precision(truth, results):
    return 0 if len(results) == 0 else sum([1 for res in results if res in truth])/len(results)

def recall(truth, results):
    return sum([1 for res in results if res in truth])/len(truth)
