from store import Document, sqlhub, connectionForURI
from vector import Vector, VectorSet

import sys, os

DB_URI = "sqlite:/tmp/memex.db"
sqlhub.processConnection = connectionForURI(DB_URI)

index = VectorSet()
for doc in Document.select():
    if doc.vector:
        index[doc.url] = Vector(map(int, doc.vector.split(",")))

for dist, url in index.nearest(index[sys.argv[1]]):
    print "%.3f\t%s" % (dist, url)
