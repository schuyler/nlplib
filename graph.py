import sys

class Graph (object):
    def __init__ (self, damp=0.85):
	self.node = {}
	self.in   = {}
	self.out  = {}
	self.damp = damp

    def add_node (self, id, weight=1.0):
	self.node[id] = weight
	self.in[id]  = []
	self.out[id] = []

    def add_edge (self, id1, id2, weight=1.0, directed=False):
	assert(id1 in self.node)
	assert(id2 in self.node)
	self.out[id1].append((id2, weight))
	self.in[id2].append((id1, weight))
	if not directed:
	    self.add_edge(id2, id1, weight, True)

    def iterate (self, prev):
	score = {}
	d = self.damp
	delta = 0.0
	for id, val in prev:
	    incoming = [prev[id2]/len(self.out[id2]) for id2,w in self.in[id]]
	    score[id] = (1-d) + d * sum(incoming)
	    delta += abs(score[id]-prev[id])
	return delta, score

    def rank (self, threshold=0.05):
	delta = sys.maxint
	score = self.nodes
	while delta > threshold:
	    delta, score = self.iterate(score)
	score = [(v,k) for k,v in score.items()]
	score.sort()
	return score
