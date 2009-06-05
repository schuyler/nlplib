from graph import TextGraph
from text import Text, HTML

import sys, textwrap, urllib2

print >>sys.stderr, ">>> starting..."

if sys.argv[1].startswith("http://"):
    text = HTML.from_url(sys.argv[1])
else:
    text = Text.from_file(sys.argv[1])
graph = TextGraph(text)
summary = graph.summary()
print "\n".join(textwrap.wrap(summary))
print
print "Tags:", ", ".join(graph.tags())
