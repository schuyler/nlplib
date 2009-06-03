import nltk

stopwords     = nltk.corpus.stopwords.words("english")
word_tokenize = nltk.tokenize.word_tokenize
sent_tokenize = nltk.data.load('tokenizers/punkt/english.pickle').tokenize
stem          = nltk.stem.PorterStemmer().stem

def stem_text (text):
    sentences = []
    for sent in sent_tokenize(text):
        tokens = word_tokenize(sent)
        words  = [w.lower() for w in tokens if w.lower() not in stopwords]
        stems  = [stem(w) for w in words]
        sentences.append(stems)
    return sentences
