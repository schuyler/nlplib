from graph import TextGraph
from text import Text

import sys, textwrap, urllib2

print >>sys.stderr, ">>> starting..."

if "://" in sys.argv[1]:
    text = Text.from_url(sys.argv[1])
else:
    text = Text.from_file(sys.argv[1])
graph = TextGraph(text)
summary = graph.summary()
print "\n".join(textwrap.wrap(summary))
print
graph = TextGraph(text)
print "Tags:", ", ".join(graph.tags())
