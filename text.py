import nltk

stopwords     = nltk.corpus.stopwords.words("english")
word_tokenize = nltk.tokenize.word_tokenize
sent_tokenize = nltk.data.load('tokenizers/punkt/english.pickle').tokenize
stem_word     = nltk.stem.PorterStemmer().stem

class Text (list):
    def __init__ (self, text):
        self.extend(sent_tokenize(text))
        self.text       = text
        self.tokens     = [word_tokenize(s) for s in self]
        self.stems      = []
        self.unstem     = {}
        for tokens in self.tokens:
            words = [w.lower() for w in tokens if w.lower() not in stopwords]
            stems = []
            for word in words:
                stem = stem_word(word)
                stems.append(stem)
                if stem not in self.unstem \
                  or len(self.unstem[stem]) > len(word):
                    self.unstem[stem] = word
            self.stems.append(stems)
        
    def __str__ (self):
        return self.text 

    def __getitem__ (self, key):
        if type(key) is int:
            return list.__getitem__(self, key)
        else:
            return self.unstem[key]

    @classmethod
    def from_file (cls, fname):
        return cls(file(fname).read())
