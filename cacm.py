from collections import namedtuple
import re
docTuple = namedtuple('docTuple', 'id, title, summary, keywords')
print(docTuple)

def parse_common_words():
    ''' Returns a generator '''
    with open('data/common_words') as f:
        common_words = (l.replace('\n', '') for l in f)
    return common_words

def parse_document():
    docs = []
    with open('data/cacm.all') as f:
        doc, id = _parse_one_doc(f)
        while doc is not None:
            docs.append(doc)
            print(doc, id)
            doc, id = _parse_one_doc(f, id)

def is_doc_end_line(l):
    return l.startswith('.I') or l == ''

def _parse_one_doc(f, id=1):
    l = f.readline()
    l = l.replace('\n', '')
    doc = None
    id = None
    title = None
    keywords = None
    summary = None
    while not is_doc_end_line(l):
        if l.startswith('.T'):
        elif l.startswith('.W'):
        elif l.startswith('.K'):
        l = f.readline()
        l = l.replace('\n', '')

    doc = docTuple('test', 'test', 'test', 123)

    if l.startswith('.I'):
        id = re.findall(r'\d+', l)[-1]
        print('END OF DOC', id)
    elif l == '':
        print('END OF FILE')
    return (doc, id)


parse_document()



