from sqlobject import *
from vector import Vector
from datetime import datetime
import sys

class BaseObject (SQLObject):
    class sqlmeta:
        lazyUpdate = True
        cacheValues = False

class Document (BaseObject):
    guid = StringCol(length=255, notNull=True, alternateID=True)
    doc_type = StringCol(length=255, notNull=True)
    tags = UnicodeCol(length=255)
    vector = BLOBCol()
    data = PickleCol(notNull=True,default={})
    doc_type_idx = DatabaseIndex('doc_type')

    def _set_vector (self, vector):
        return self._SO_set_vector(vector.tostring())

    def _get_vector (self):
        vector = Vector()
        vector.fromstring(self._SO_get_vector())
        return vector

    def _set_tags (self, tags):
        return self._SO_set_tags(",".join(tags))

    def _get_tags (self, thunk):
        return self._SO_get_tags().split(u",")

class Link (BaseObject):
    source = ForeignKey("Document")
    target = ForeignKey("Document")

class Feed (BaseObject):
    document     = ForeignKey('Document', alternateID=True)
    digest       = StringCol(length=40)
    fetched_at   = DateTimeCol()
    interval     = IntCol(default=3600)

if __name__ == "__main__":
    import sys
    sqlhub.processConnection = connectionForURI("sqlite:" + sys.argv[1])
    Document.createTable()

