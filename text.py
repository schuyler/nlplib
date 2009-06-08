import language, stem
import re, urllib2

nonword       = re.compile(r'\W+')
stem_word     = stem.Stemmer("en").stemWord
stopwords     = language.WordList("stopwords.txt").words
whitespace    = re.compile(r'\s+')
word_tokenize = lambda s: whitespace.split(s)

lc = language.LanguageChecker()
sent_tokenize = lc.find_sentences

class Text (list):
    def __init__ (self, text):
        text = whitespace.sub(" ", text)
        self.extend(sent_tokenize(text))
        self.text       = " ".join(self)
        self.tokens     = filter(None, [word_tokenize(s) for s in self])
        self.stems      = []
        self.unstem     = {}
        self.stem()
    
    def stem (self):
        unstem = {}
        for tokens in self.tokens:
            words = [nonword.sub("", w.lower()) for w in tokens]
            words = filter(lambda w: w not in stopwords, words)
            stems = []
            for word in words:
                stem = stem_word(word)
                if not stem: continue
                stems.append(stem)
                unstem.setdefault(stem, {})
                unstem[stem].setdefault(word, 0)
                unstem[stem][word] += 1
            self.stems.append(stems)
        for stem, words in unstem.items():
            words = sorted([(c,w) for w,c in words.items()])
            self.unstem[stem] = words[-1][1]
        
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

    @classmethod
    def from_url (cls, url):
        request = urllib2.Request(url)
        request.add_header("User-Agent","Mozilla/5.0 (compatible)")
        page = urllib2.build_opener().open(request).read()
        try:
            page = page.decode("utf-8")
        except UnicodeDecodeError:
            page = page.decode("latin-1")
        return cls(page)
