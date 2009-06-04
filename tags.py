from graph import TextGraph
from text import Text

import sys, textwrap

text = Text.from_file(sys.argv[1])
graph = TextGraph(text)
summary = graph.summary()
print "\n".join(textwrap.wrap(summary))
print
print "Tags:", ", ".join(graph.tags())
