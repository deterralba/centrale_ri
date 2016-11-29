from collections import namedtuple
import re
docTuple = namedtuple('docTuple', 'id, title, summary, keywords')

def _get_line(f):
    l = f.readline()
    l = l.replace('\n', ' ')
    return l

def parse_common_words():
    with open('data/common_words') as f:
        common_words = list(l.replace('\n', '') for l in f)
    return common_words

def parse_document():
    docs = []
    with open('data/cacm.all') as f:
        doc, next_id = _parse_one_doc(f)
        while next_id is not None:
            doc, next_id = _parse_one_doc(f, next_id)
            docs.append(doc)
    return docs

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
        next_id = re.findall(r'\d+', l)[-1]
        # print('id:{} - END OF DOC - next id: {}'.format(id, next_id))
    elif l == '':
        next_id = None
        # print('END OF FILE')
    else:
        raise ValueError('We should not be here')
    return (doc, next_id)

def tokenize(doc):
    tokens = []
    for field in doc:
        tok = field.split()
        for sp in '-,.\/[]()?!\'"+=<>*':
            tok = [t for to in tok for t in to.split(sp)]
        tok = [t.lower() for t in tok]
        tok = [t for t in tok if tok != '']
        tokens.extend([t for t in tok if t != ''])
        # for sub in '' :
        #    tok = [t.replace(sub, '') for t in tok]
        # print(tok)
    tokens = list(set(tokens))
    return tokens

def get_number_of_tokens():
    docs = parse_document()
    common_words = list(parse_common_words())
    tokens = [t for doc in docs for t in tokenize(doc)]
    print('Number of tokens (after lower/ ponctuation and basic duplicate removal): {}'.format(len(tokens)))
    tokens = list(set(tokens))
    print('Number of tokens (after removing duplicates): {}'.format(len(tokens)))
    tokens = [t for t in tokens if t not in common_words]
    print('Number of tokens (after removing {} common words): {}'.format(len(common_words), len(tokens)))
    input('Type something to see the tokens')
    print(tokens)

if __name__ == '__main__':
    get_number_of_tokens()

