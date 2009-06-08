from store import sqlhub, connectionForURI
from loader import Feed

import sys, socket

DB_URI = "sqlite:/tmp/memex.db"
sqlhub.processConnection = connectionForURI(DB_URI)
socket.setdefaulttimeout(3)

print >>sys.stderr, ">>> starting..."

if len(sys.argv) > 1:
    feeds = sys.argv[1:]
else:
    feeds = map(str.strip, sys.stdin.readlines())

loader = Feed()
for feed in feeds:
    loader.fetch(feed, loader.add)
