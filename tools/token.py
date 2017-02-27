from nltk.stem import WordNetLemmatizer

wnl = WordNetLemmatizer()

def extract_tokens(string):
    for sp in '-,.\/[]()?!\'"+=<>*:^':
        string = string.replace(sp, ' ')
    return string.split()

def filter_tokens_with_card(tokens, common_words):
    ''' Returns {(token, cardinal of token in tokens), ...} '''
    words = [w.lower() for w in tokens]
    words = [w for w in words if len(w) > 1 and w not in common_words]
    global wnl
    words = [wnl.lemmatize(w) for w in words]
    couples = {(w, words.count(w)) for w in words}
    return couples

def filter_tokens(tokens, common_words, remove_common, lemm):
    words = [w.lower() for w in tokens]
    words = [w for w in words if len(w) > 1]
    if remove_common:
        words = [w for w in words if w not in common_words]
    if lemm:
        global wnl
        words = [wnl.lemmatize(w) for w in words]
    return set(words)

def get_all_tokens(docs, common_words, collection, print_res=False, lemm=True):
    tokens = [t for doc in docs.values() for t in collection.tokenize_doc(doc, common_words, remove_common=False, lemm=lemm)]
    print('Number of tokens (after lower/ ponctuation and basic duplicate removal): {}'.format(len(tokens)))
    tokens = list(set(tokens))
    print('Number of tokens (after removing duplicates): {}'.format(len(tokens)))
    tokens = [t for t in tokens if t not in common_words]
    print('Number of tokens (after removing {} common words): {}'.format(len(common_words), len(tokens)))
    if print_res:
        input('Type something to see the tokens')
        print(tokens)
    return tokens
