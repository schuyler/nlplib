from hashlib import md5
from array import array
from struct import unpack
from heapq import heappush, heappop

class Vector (array):
    """
    >>> Vector((1,2,3))
    <1, 2, 3>
    >>> Vector((1,2,3)) | Vector((4,5,6))
    <1, 2, 3, 4, 5, 6>
    >>> Vector((1,2,3)) & Vector((4,5,6))
    <>
    >>> Vector((1,2,3)) & Vector((2,3,4))
    <2, 3>
    >>> Vector((1,2,3)) ^ Vector((2,3,4))
    <1, 4>
    >>> Vector((1,2,3)) - Vector((2,3,4))
    <1>
    >>> Vector((2,3,4)) - Vector((1,2,3))
    <4>
    >>> Vector((1,2,3)) % Vector((1,2,3))
    0
    >>> Vector((1,2,3)) % Vector((2,3,4))
    2
    >>> Vector((1,2,3)) % Vector((4,5,6))
    6
    """
    def __new__ (cls, values=(), typecode="H"):
        return super(Vector,cls).__new__(cls, typecode, sorted(set(values)))

    @classmethod
    def fromtokens (cls, tokens, n=4):
        vect = cls()
        values = []
        for token in tokens:
            ints = unpack("8"+vect.typecode, md5(token).digest())[:n]
            values.extend(ints)
        vect.extend(sorted(set(values)))
        return vect

    @classmethod
    def fromtext (cls, txt, n=4):
        return cls.fromtokens(map(str.strip, txt.split()), n)

    def __and__ (self, other):
        intersect = []
        i = j = 0
        while i < len(self):
            while j < len(other):
                if self[i] < other[j]: break
                if self[i] == other[j]:
                    intersect.append(self[i])
                j += 1
            i += 1
        return type(self)(intersect)

    def __sub__ (self, other):
        remain = []
        i = j = 0
        while i < len(self) and j < len(other):
            if self[i] < other[j]:
                remain.append(self[i])
                i += 1
            elif self[i] > other[j]:
                j += 1
            else:
                i += 1
                j += 1
        if i < len(self):
            remain.extend(self[i:])
        return type(self)(remain)

    def __or__ (self, other, exclusive=False):
        merged = []
        i = j = 0
        while i < len(self) and j < len(other):
            if self[i] < other[j]:
                merged.append(self[i])
                i += 1
            elif self[i] > other[j]:
                merged.append(other[j])
                j += 1
            else:
                if not exclusive:
                    merged.append(self[i])
                i += 1
                j += 1
        if i < len(self):
            merged.extend(self[i:])
        elif j < len(other):
            merged.extend(other[j:])
        return type(self)(merged)

    __add__ = __or__

    def __xor__ (self, other):
        return self.__or__(other, True)

    def __mod__ (self, other):
        return len(self ^ other)

    __floordiv__ = __mod__

    def __div__ (self, other):
        return len(self ^ other) / float(len(self) + len(other))

    def __hash__ (self):
        return tuple(self).__hash__()

    def __repr__ (self):
        return "<" + ", ".join(map(str,self)) + ">"
        
class VectorSet (dict):
    """
    >>> strings = (
    ...   "hello everyone",
    ...   "everyone is having a great time",
    ...   "time is the great enemy",
    ...   "I don't have time for that",
    ...   "where did you find that?",
    ...   "where can I find everyone?",
    ...   "hello I am having lunch"
    ... )
    >>> v = VectorSet()
    >>> for i in range(len(strings)): v[i] = Vector.fromtext(strings[i]) 
    >>> v.nearest(v[0], 3)
    [(0, 0), (20, 6), (24, 1)]
    >>> v.nearest(v[1], 3)
    [(0, 1), (20, 2), (24, 0)]
    >>> v.nearest(v[2], 3)
    [(0, 2), (20, 1), (28, 0)]
    >>> v.nearest(v[3], 3)
    [(0, 3), (32, 0), (36, 2)]
    >>> v.nearest(v[4], 3)
    [(0, 4), (24, 5), (28, 0)]
    >>> v.nearest(v[5], 3)
    [(0, 5), (24, 4), (28, 0)]
    >>> v.nearest(v[6], 3)
    [(0, 6), (20, 0), (32, 5)]
    """
    def __setitem__ (self, key, vector):
        assert isinstance(vector, Vector)
        dict.__setitem__(self, key, vector)

    def nearest (self, vector0, n=10):
        heap = []
        for id, vector in self.items():
            heappush(heap, (vector0 / vector, id))
        return [heappop(heap) for i in range(min(n, len(heap)))]

if __name__ == "__main__":
    import doctest
    doctest.testmod()
