from collections import namedtuple, defaultdict
from nltk.stem import WordNetLemmatizer
import re
docTuple = namedtuple('docTuple', 'id, title, summary, keywords')
wnl = WordNetLemmatizer()

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
        next_id = int(re.findall(r'\d+', l)[-1])
        # print('id:{} - END OF DOC - next id: {}'.format(id, next_id))
    elif l == '':
        next_id = None
        # print('END OF FILE')
    else:
        raise ValueError('We should not be here')
    return (doc, next_id)

def tokenize(field, remove_common, lemm):
    global wnl
    words = field.split()
    for sp in '-,.\/[]()?!\'"+=<>*:^':
        words = [w for word in words for w in word.split(sp)]
    words = [w.lower() for w in words]
    words = [w for w in words if len(w) > 1]
    if remove_common:
        words = [w for w in words if w not in common_words]
    if lemm:
        words = [wnl.lemmatize(w) for w in words]
    return set(words)

def tokenize_doc(doc, remove_common, lemm):
    tokens = [t for field in doc[1:] for t in tokenize(field, remove_common, lemm)]
    return set(tokens)

def get_all_tokens(docs, common_words, print_res=False):
    tokens = [t for doc in docs for t in tokenize_doc(doc, remove_common=False, lemm=True)]
    print('Number of tokens (after lower/ ponctuation and basic duplicate removal): {}'.format(len(tokens)))
    tokens = list(set(tokens))
    print('Number of tokens (after removing duplicates): {}'.format(len(tokens)))
    tokens = [t for t in tokens if t not in common_words]
    print('Number of tokens (after removing {} common words): {}'.format(len(common_words), len(tokens)))
    if print_res:
        input('Type something to see the tokens')
        print(tokens)
    return tokens

def index_doc(index_dict, doc):
    tokens = tokenize_doc(doc, remove_common=True, lemm=True)
    for t in tokens:
        index_dict[t] |= {doc.id}

def search(all_docs):
    print('Type your query (intersection is shown if several words are typed)')
    q = input('> ')
    if q.startswith('!'):
        q = q[1:]
        q = q.strip()
        try:
            id = int(q)
            print(id)
            doc_list= [d for d in all_docs if d.id == id]
            if not doc_list:
                print('No doc with the given id')
                search(all_docs)
            doc = doc_list[0]
            print('Document found: ', doc)
            print('Tokens extracted:')
            print(tokenize_doc(doc, remove_common=True, lemm=True))
            search(all_docs)
        except IOError:
            print('! must be followed by a number')
            search(all_docs)
    else:
        tokens = tokenize(q, remove_common=True, lemm=True)
        print('Terms searched: ', *tokens)
        if not tokens:
            print('Only common words or ponctuations were given. Try again.')
            search(all_docs)
        docs = []
        for t in tokens:
            docs.append(index_dict[t])
        res = docs[0]
        for doc in docs[1:]:
            res &= doc
        if res:
            res = sorted(res)
            print('Documents\'ids found (type !id to see document details):')
            print(*res, sep=', ')
        else:
            print('No results were found')
        search(all_docs)

if __name__ == '__main__':
    print('Parsing cacm.all')
    all_docs = parse_document()
    print('Parsing common_words')
    common_words = parse_common_words()

    '''
    docs1 = docs[:len(docs)//2]
    docs2 = docs[len(docs)//2:]
    get_all_tokens(docs1, common_words)#, print_res=True)
    get_all_tokens(docs2, common_words)
    '''
    # all_tokens = get_all_tokens(all_docs, common_words)

    print('Building the index')
    index_dict = defaultdict(set)
    for doc in all_docs:
        index_doc(index_dict, doc)
    print('Done!')
    # print(index_dict)

    search(all_docs)


