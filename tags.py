from graph import Graph
from stem import stem_text

import sys

text = file(sys.argv[1]).read()

graph = Graph()
sentences = stem_text(text)
for i in range(len(sentences)):
    graph.add_node(i)
    for stem in sentences[i]:
        graph.add_node(stem)
        graph.add_edge(stem, i)

scored = graph.rank()
print scored

