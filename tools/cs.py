'''
NB: Work in progress: CS276 is not yet integrated
'''
# TODO: parse cs276

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

def parse_document():
    docs_dict = dict()
    with open('data/cacm.all') as f:
        doc, next_id = _parse_one_doc(f)
        while next_id is not None:
            doc, next_id = _parse_one_doc(f, next_id)
            docs_dict[doc.id] = doc
    return docs_dict

def _is_doc_end_line(l):
    return l.startswith('.I') or l == ''

def _parse_one_doc(f, id=1):
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
    tokens = {t for field in doc[1:]
              for t in tk.filter_tokens(tk.extract_tokens(field), common_words, remove_common, lemm)}
    return tokens

def tokenize_doc_with_freq(doc, common_words):
    couples_dict = defaultdict(lambda: [0, 0])
    for field in doc[1:]:
        tokens_and_freq = tk.filter_tokens_with_freq(tk.extract_tokens(field), common_words)
        for t, freq in tokens_and_freq:
            couples_dict[t] = [t, couples_dict[t][1] + freq]
    couples = set(tuple(couple) for couple in couples_dict.values())
    return couples

