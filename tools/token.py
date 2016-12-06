from nltk.stem import WordNetLemmatizer

wnl = WordNetLemmatizer()

def extract_tokens(string):
    for sp in '-,.\/[]()?!\'"+=<>*:^':
        string = string.replace(sp, ' ')
    return string.split()

def filter_tokens_with_freq(tokens, common_words):
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

