import sys, math

class Graph (object):
    def __init__ (self, damp=0.85):
        self.edge = {}
        self.damp = damp

    def add_edge (self, id1, id2, weight=1.0):
        for a, b in (id1,id2), (id2,id1):
            self.edge.setdefault(a, {})
            self.edge[a].setdefault(b, 0.0)
            self.edge[a][b] += weight

    def iterate (self, prev):
        score = {}
        d = self.damp
        delta = 0.0
        for id, val in prev.items():
            incoming = 0.0
            for id2, weight in self.edge[id].items():
                incoming += prev[id2] * self.edge[id2][id]
            score[id] = (1-d) + d * incoming
            delta += abs(score[id]-prev[id])
        return delta, score

    def normalize (self):
        for id, weights in self.edge.items():
            total = sum(weights.values())
            for id2 in weights.keys():
                self.edge[id][id2] /= total

    def rank (self, threshold=0.1, max_iterations = 15):
        self.normalize()
        delta = sys.maxint
        score = dict([(id, 1.0) for id in self.edge])
        iterations = 0
        while delta > threshold and iterations < max_iterations:
            iterations += 1
            delta, score = self.iterate(score)
            #print "iteration", iterations, delta
        score = [(v,k) for k,v in score.items()]
        return list(reversed(sorted(score)))

class TextGraph (Graph):
    def __init__ (self, text):
        Graph.__init__(self)
        self.text = text
    
    def rank_stems (self):
        for sentence in self.text.stems:
            for i in range(len(sentence)-1):
                for j in range(i, len(sentence)):
                    #print sentence[i], sentence[j]
                    if sentence[i] != sentence[j]:
                        self.add_edge(sentence[i], sentence[j])
        return self.rank()

    def rank_sentences (self):
        terms = {}
        for i in range(len(self.text.stems)):
            for stem in self.text.stems[i]:
                terms.setdefault(stem, [])
                for j in terms[stem]:
                    if i != j: self.add_edge(i, j)
                terms[stem].append(i)
        return self.rank()

    def rank_keywords (self):
        ranked = self.rank_stems()
        return [(w,self.text[s]) for w,s in ranked]

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
