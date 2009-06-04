import sys

class Graph (object):
    def __init__ (self, damp=0.85):
        self.node = {}
        self._in  = {}
        self.out  = {}
        self.damp = damp

    def add_node (self, id, weight=1.0):
        if id not in self.node:
            self.node[id] = weight
            self._in[id]  = set()
            self.out[id]  = set()

    def add_edge (self, id1, id2, weight=1.0, directed=False):
        assert(id1 in self.node)
        assert(id2 in self.node)
        self.out[id1].add((id2, weight))
        self._in[id2].add((id1, weight))
        if not directed:
            self.add_edge(id2, id1, weight, True)

    def iterate (self, prev):
        score = {}
        d = self.damp
        delta = 0.0
        for id, val in prev.items():
            incoming = [prev[id2]/len(self.out[id2]) for id2,w in self._in[id]]
            score[id] = (1-d) + d * sum(incoming)
            delta += abs(score[id]-prev[id])
        return delta, score

    def rank (self, threshold=0.05):
        delta = sys.maxint
        score = self.node
        while delta > threshold:
            delta, score = self.iterate(score)
        score = [(v,k) for k,v in score.items()]
        return list(reversed(sorted(score)))

class TextGraph (Graph):
    def __init__ (self, text):
        Graph.__init__(self)
        self.ranked = None
        self.text   = text
        for i in range(len(text)):
            self.add_node(i)
            for stem in text.stems[i]:
                self.add_node(stem)
                self.add_edge(stem, i)

    def rank_sentences (self, t=0.05):
        if not self.ranked: self.ranked = self.rank(t)
        return [(w,s) for w,s in self.ranked if type(s) is int]

    def rank_stems (self, t=0.05):
        if not self.ranked: self.ranked = self.rank(t)
        return [(w,s) for w,s in self.ranked if type(s) is not int]

    def rank_keywords (self, t=0.05):
        if not self.ranked: self.ranked = self.rank(t)
        return [(w,self.text[s]) for w,s in self.ranked
                                 if type(s) is not int]

    def summary (self, max_length=250):
        items = []
        length = 0
        for score, n in self.rank_sentences():
            items.append(n) 
            length += len(self.text[n])
            if length >= max_length: break
        items.sort()
        return " ".join([self.text[n] for n in items])

    def tags (self, count=7):
        return [kw for score, kw in self.rank_keywords()[:count]]
