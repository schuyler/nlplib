import nltk
import re, urllib2

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
        self.stem()
    
    def stem (self):
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

from html import html2text_file
class HTML (Text):
    def __init__ (self, html):
        try:
            html = html.decode("utf-8")
        except UnicodeDecodeError:
            html = html.decode("latin-1")
        # turn the html into markdown
        markdown = html2text_file(html, None)
        text = [t for t in markdown.split("\n\n")
                    # if it starts with a word char
                    if re.match("^\w", t)
                    # and it contains something sentence-like
                    and re.search("[A-Z][^\.!?]+[\.!?]", t)]
        text = "\n".join(text)
        # get rid of markdown link references
        text = re.sub("\[\d*\]", "", text)
        text = re.sub("[\[\]]", "", text)
        Text.__init__(self, text)
        self.text = markdown

    @classmethod
    def from_url (cls, url):
        request = urllib2.Request(url)
        request.add_header("User-Agent","Mozilla/5.0 (compatible)")
        page = urllib2.build_opener().open(request).read()
        return cls(page)

