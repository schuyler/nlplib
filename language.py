import sys, re, os, random

BASE = os.path.dirname(__file__)

class WordList (object):
    def __init__ (self, path):
        self.words = {}
        if not path.startswith("/"): path = os.path.join(BASE,path)
        for line in file(path).readlines():
            if line.strip(): self.words[line.strip()] = True

    def find (self, tokens):
        return filter(lambda w: w.lower() in self.words, tokens)

    def list (self):
        return self.words.keys()

    def random (self):
        return random.sample(self.list(), 1)[0]

class LanguageChecker (object):
    entities = { "nbsp": " ",
                 "amp":  "&",
                 "gt":   ">",
                 "lt":   "<",
                 "quot": '"',
                 "8217": "'", # there must be a better way of doing this
                 "8216": "'",
                 "8220": '"',
                 "8221": '"' }

    code_tags  = re.compile(r'<(script|style|noscript).+?</\1>', re.I|re.S)
    block_tags = re.compile(r'</?(?:applet|blockquote|body|button|div|dl|fieldset|form|frameset|h[1-6]|head|html|iframe|img|layer|legend|object|ol|p|select|table|ul|tr|td|th)(?!\w)[^>]*?>', re.I|re.S)
    sentence_end = re.compile(r'[.!?][])"]?(?:\s|$)',re.S)

    word_boundary = re.compile("[*(){}[\]:;,.!?~\s]+",re.S)
    html_tag = re.compile("<[^>]+>",re.S)
    html_element = re.compile(r"<([^>])+>.+?</\1>",re.S)
    html_entity = re.compile("&#?(\w+);")
    dict_file = "/usr/share/dict/words"

    def __init__ (self):
        self.words = WordList(self.dict_file)

    def fix_entities (self, match):
        text = match.group(1)
        if text in self.entities:
            return self.entities[text]
        try:
            return unichr(int(text))
        except ValueError:
            pass
        try:
            return unichr(int("0" + text, 16))
        except ValueError:
            pass
        return ""

    def split_html (self, html):
        html = self.code_tags.sub('', html)
        return self.block_tags.split(html)

    def strip_html (self, text):
        cleaned = self.html_tag.sub(" ", text)
        return self.html_entity.sub(self.fix_entities, cleaned)

    def find_text_blocks (self, html):
        blocks = map(self.strip_html, self.split_html(html))
        return [block for block in blocks if self.sentence_end.search(block)] 

    sentence = re.compile(
        r'(\w(?:[^!?.]|(?<=\b[a-z])\.)+[!?.]+)(?![a-z]{1,4}\.\s)', re.I)
    word     = re.compile(r'\w+')
    def split_sentences (self, text):
        return filter(self.word.match, self.sentence.split(text))

    def find_sentences (self, text):
        sentences = []
        if self.html_element.search(text):
            blocks = self.find_text_blocks(text)
        else:
            blocks = [text]
        for block in blocks:
            sentences.extend(self.split_sentences(block))
        return [x.strip() for x in sentences]

    def is_english (self, text):
        tokens = self.word_boundary.split(text)
        if not tokens: return False
        ok = self.words.find(tokens)
        return (len(ok) / float(len(tokens))) > .5

class WikipediaChecker (LanguageChecker):
    p_tag   = re.compile(r'<p(?!\w)[^>]*?>(?!<small>)(.+?)</p>', re.I)
    sup_tag = re.compile(r'<sup(?!\w)[^>]*?>(.+?)</sup>', re.I)
    parens  = re.compile(r'\s*\([^)]+\)')

    def find_text_blocks (self, html):
        blocks = [self.sup_tag.sub("",x) for x in self.p_tag.findall(html)]
        #blocks = [self.parens.sub("",x) for x in blocks]
        blocks = [self.strip_html(x) for x in blocks]
        return [block for block in blocks if self.sentence_end.search(block)] 

if __name__ == "__main__":
    import urllib2,sys
    title = re.sub(" ","_",sys.argv[1])
    request = urllib2.Request(
        "http://en.wikipedia.org/w/index.php?title=%s&printable=yes"%title)
    request.add_header("User-Agent","Mozilla/5.0 (compatible)")
    page = urllib2.build_opener().open(request).read()
    check = WikipediaChecker()
    for block in check.find_text_blocks(page): print block,"\n"
