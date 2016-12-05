import time
from functools import reduce
import tools.token as tk
import tools.cacm as cacm

def search(all_docs, common_words, binary_index):
    print('Type your query (intersection is shown if several words are typed)')
    q = input('> ')
    start_time = time.time()
    if q.startswith('!'):
        reverse_search(all_docs, common_words, q[1:])
    else:
        tokens = tk.tokenize_string(q, common_words, remove_common=True, lemm=True)
        if not tokens:
            print('Only common words or ponctuations were given. Try again.')
        else:
            print('Terms searched: ', *tokens)
            docs = [binary_index[t] for t in tokens]
            res = reduce(lambda x, y: x&y, docs)
            if res:
                res = sorted(res)
                print('{} documents found (type !id to see document details):'.format(len(res)))
                print(*res, sep=', ')
            else:
                print('No results were found')
    print('Searching took {:.2f}ms.'.format((time.time() - start_time)*1000))

def reverse_search(all_docs, common_words, q):
    try:
        id = int(q.strip())
        doc = next(d for d in all_docs if d.id == id)
        print('Document found: ', doc)
        print('Tokens extracted:\n ', cacm.tokenize_doc(doc, common_words, remove_common=True, lemm=True))
    except StopIteration:
        print('No doc with id ', id)
    except (IOError, ValueError):
        print('! must be followed by a number')


