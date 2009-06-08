from text import Text
from store import Document, Link
from graph import TextGraph
from vector import Vector

import urllib2, sys
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

class Loader (object):
    Reload_Min = 75
    Reload_Max = 86400 * 14
    doc_type = "text/plain"

    def __init__ (self, proxy=None):
        self.proxy = proxy

    def add (self, guid, content=None, source=None):
        print >>sys.stderr, "Adding '%s' (%s)" % (title, url)
        try:
            doc = Document.byGuid(guid)
        except:
            doc = Document(guid=guid, doc_type=self.doc_type)
            Link(source=source, target=doc)
        if content and not doc.data:
            data, tags, vector = self.process(content) 
            doc.data = data
            doc.vector = vector
            doc.tags = tags
            doc.sync()
        return doc

    def extract (self, content):
        return content

    def process (self, content, tag_count=7, doc_count=25):
        text      = Text(self.extract(content))
        graph     = TextGraph(text)
        key_stems = [kw for score, kw in graph.rank_stems()]
        tags      = [text[kw] for kw in key_stems[:tag_count]]
        vector    = Vector.fromtokens(key_stems[:doc_count])
        data      = {"content":content, "text":text.text}
        return data, tags, vector

    def load (self, doc, content):
        self.add(doc.url, content)

    def decode (self, content):
        try:
            content = content.decode("utf-8")
        except UnicodeDecodeError:
            content = content.decode("latin-1")
        return content

    def fetch (self, doc, callback):
        if self.proxy:
            self.proxy.fetch(doc, callback)
            return
        if hasattr(doc, "url"):
            url = doc.url
        else:
            url = doc
        request = urllib2.Request(url)
        request.add_header("User-Agent","Mozilla/5.0 (compatible)")
        try:
            page = urllib2.build_opener().open(request).read()
        except urllib2.URLError:
            return
        page = self.decode(page)
        callback(doc, page) 
