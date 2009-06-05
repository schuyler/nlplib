from store import Document, sqlhub, connectionForURI
from vector import Vector
from graph import TextGraph
from text import Text

import sys, textwrap, urllib2, os

DB_URI = "sqlite:/tmp/memex.db"
sqlhub.processConnection = connectionForURI(DB_URI)

print >>sys.stderr, ">>> starting..."

for line in sys.stdin.readlines():
    url = line.strip()
    print >>sys.stderr, ">>> reading", url
    if url.startswith("http://"):
        text = Text.from_url(url)
        content_type = "text/html"
    else:
        text = Text.from_file(url)
        content_type = "text/plain"
    graph = TextGraph(text)
    #summary = graph.summary()
    #print "\n".join(textwrap.wrap(summary))
    #print
    #print "Tags:", ", ".join(graph.tags())
    tags = ",".join(graph.tags(7))
    v_tags = graph.tags(25)
    vector = Vector.fromtokens(v_tags)
    v_string = ",".join(map(str, vector))
    Document(
        title=url,
        description=text.text,
        url=url,
        source=url,
        content_type=content_type,
        tags=tags,
        vector=v_string,
        current=True,
        revision=1)
    print "tags: ", tags    
