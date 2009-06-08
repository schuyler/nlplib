#!/usr/bin/python

import sys, os
from heapq import heappush, heappop
from datetime import datetime, timedelta

from twisted.internet import reactor, task
from twisted.web import client
from twisted.python import log

project = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project)

from store import Document, sqlhub, connectionForURI
from loader import Loader, Feed

DB_URI = "sqlite:/tmp/memex.db"
sqlhub.processConnection = connectionForURI(DB_URI)

class Crawler (object):
    AGENT_STRING    = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.11) "+\
                      "Gecko/20041107 Firefox/2.0.0"
    HTTP_TIMEOUT    = 15
    loader_classes  = (Loader, Feed)

    def __init__ (self):
        self.running    = 0
        self.concurrent = 10
        self.queue      = []
        self.loader     = {}
        self.refresh    = datetime.now()
        for cls in self.loader_classes:
            self.loader[cls.doc_type] = cls(proxy=self)

    def schedule (self):
        self.refresh = datetime.now() + timedelta(seconds=Loader.Reload_Min)
        self.queue = []
        for doc in Document.select(Document.q.interval > 0):
            if doc.fetched_at:
                event = doc.fetched_at + timedelta(seconds=doc.interval)
            else:
                event = datetime.now()
            loader = self.loader[doc.doc_type]
            heappush(self.queue, (event, doc, loader.load))
        log.msg("%d events scheduled." % len(self.queue))

    def poll (self):
        while self.queue and self.running < self.concurrent:
            if self.queue[0][0] > datetime.now(): break
            event, doc, callback = heappop(self.queue)
            self.request(doc, callback)
            self.running += 1
        if not self.running and self.refresh < datetime.now():
            self.schedule()
            
    def fetch (self, doc, callback):
        heappush(self.queue, (datetime.now(), doc, callback))

    def request (self, doc, callback):
        if hasattr(doc, "url"):
            url = doc.url.encode("utf-8")
        else:
            url = doc.encode("utf-8")
        df = client.getPage(url=url, agent=self.AGENT_STRING, timeout=self.HTTP_TIMEOUT)
        df.addCallback(self.done_fetching, doc, callback)
        df.addErrback(self.error_fetching, url)
    
    def done_fetching (self, content, doc, callback):
        try:
            content = content.decode("utf-8")
        except UnicodeDecodeError:
            content = content.decode("latin-1")
        callback(doc, content)
        self.running -= 1 

    def error_fetching (self, failure, url):
        log.msg("got error from %s: %s" % (url, failure.getErrorMessage()))
        self.running -= 1 

if __name__ == "__main__":
    log.startLogging(sys.stderr)
    crawler = Crawler()
    if len(sys.argv) > 1:
        if sys.argv[1] == "-":
            feeds = map(str.strip, sys.stdin.readlines())
        else:
            feeds = sys.argv[1:]
        loader = Feed(proxy=crawler)
        for feed in feeds:
            crawler.fetch(feed, loader.add)
    t = task.LoopingCall(crawler.poll)
    t.start(1.0)
    reactor.run()
