from store import Feed
from base import Loader

import feedparser, datetime

class Feed (Loader):
    def add (self, guid, content=None, source=None):
        content = feedparser.parse(content.encode("utf-8"))
        doc = Loader.add(self, guid, content.feed)
        self.load(doc, content)

    def extract (self, content):
        return ". ".join([content.get(i,"") for i in ("title", "description")])

    def process (self, content):
        data, tags, vector = Loader.process(self, content)
        content["text"] = data["text"]
        return content, tags, vector

    def update (self, doc, content):
        try:
            feed = Feed.byDocument(doc)
        except:
            feed = Feed(document=doc)
        digest = self.digest(content)
        if feed.digest == digest:
            feed.interval = min(feed.interval * 2, self.Reload_Max)
            do_load = False
        else:
            feed.interval = max(feed.interval / 2, self.Reload_Min)
            feed.digest = digest
            do_load = True
        feed.fetched_at = datetime.datetime.now()
        feed.sync()
        return do_load

    def load (self, doc, content):
        if not self.update(doc, content): return
        feed = feedparser.parse(content.encode("utf-8"))
        loader = FeedItem(proxy=self.proxy)
        for item in feed.entries:
            loader.add(item.id, item, source)

class FeedItem (Feed):
    def add (self, guid, content, source):
        doc = Loader.add(self, guid, content, source)
        if content.get("link"):
            Loader(proxy=self.proxy).add(content.link, None, doc)
        return doc
