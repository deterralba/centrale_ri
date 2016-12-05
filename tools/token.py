from nltk.stem import WordNetLemmatizer

wnl = WordNetLemmatizer()

def extract_tokens(string):
    for sp in '-,.\/[]()?!\'"+=<>*:^':
        string = string.replace(sp, ' ')
    return string.split()

def tokenize_string_with_freq(field, common_words):
    words = extract_tokens(field)
    words = [w.lower() for w in words]
    words = [w for w in words if len(w) > 1 and w not in common_words]
    global wnl
    words = [wnl.lemmatize(w) for w in words]
    couples = {(w, words.count(w)) for w in words}
    return couples

def tokenize_string(field, common_words, remove_common, lemm):
    words = extract_tokens(field)
    words = [w.lower() for w in words]
    words = [w for w in words if len(w) > 1]
    if remove_common:
        words = [w for w in words if w not in common_words]
    if lemm:
        global wnl
        words = [wnl.lemmatize(w) for w in words]
    return set(words)

