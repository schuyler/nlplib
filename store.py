from vector import Vector
from datetime import datetime
import sys, sqlite3, cPickle

class connect (object):
    _db = None

    def __init__ (self, *args, **kwargs):
        if not self._db:
            db = sqlite3.connect(*args, **kwargs)
            db.row_factory = sqlite3.Row
            db.isolation_level = None
            self.__class__._db = db

    @classmethod
    def query (cls, sql, args=()):
        cursor = cls._db.cursor()
        cursor.execute(sql, args)
        return cursor.fetchall()

    @classmethod
    def execute (cls, sql, args=()):
        cursor = cls._db.cursor()
        cursor.execute(sql, args)
        rowid = cursor.lastrowid 
        return rowid

class BaseObject (object):
    _ddl = None

    def __init__ (self, **attrs):
        self.id = None
        for key, value in attrs.items():
            self._columns = attrs.keys()
            setattr(self, key, value)
    
    def _table (self):
        return self.__class__.__name__.lower()

    def _values (self):
        values = []
        for key in self._columns:
            if hasattr(self, "_get_" + key):
                values.append(getattr(self, "_get_" + key)())
            else:
                values.append(getattr(self, key))
        return values

    def update (self):
        if not self.id:
            raise KeyError("object not created yet")
        placeholder = ", ".join([k+"=?" for k in self._columns])
        sql = "update %s set %s where id=?;" % (
                    self._table(), placeholder)
        connect.execute(sql, self._values() + [self.id])

    def create (self):
        if self.id:
            raise KeyError("object already created")
        cols = ",".join(self._columns)
        placeholder = ",".join(["?"] * len(self._columns))
        sql = "insert into %s (%s) values (%s);" % (
                    self._table(), cols, placeholder)
        self.id = connect.execute(sql, self._values())
        
    @classmethod
    def select (cls, where=None, args=()):
        sql = "select * from %s" % cls.__name__.lower()
        if where: sql += " where %s" % where
        items = []
        for row in connect.query(sql, args):
            attrs = dict(zip(row.keys(), row))
            for key, val in attrs.items():
                if hasattr(cls, "_set_" + key):
                    attrs[key] = getattr(cls, "_set_" + key)(val)
            items.append(cls(**attrs))
        return items

    @classmethod
    def create_table (cls):
        connect.execute(cls._ddl)

class Document (BaseObject):
    _ddl = """
        CREATE TABLE document (
            id INTEGER PRIMARY KEY,
            guid VARCHAR(255),
            doc_type VARCHAR(255),
            vector BLOB,
            data BLOB
        );
    """
    def _get_vector (self):
        return self.vector.tostring()

    @classmethod
    def _set_vector (self, data):
        vector = Vector()
        vector.fromstring(data)
        return vector

    def _get_data (self):
        return cPickle.dumps(self.data)

    @classmethod
    def _set_data (self, data):
        return cPickle.loads(data.encode("utf-8"))

"""
class Link (BaseObject):
    source = ForeignKey("Document")
    target = ForeignKey("Document")

class Feed (BaseObject):
    document     = ForeignKey('Document', alternateID=True)
    digest       = StringCol(length=40)
    fetched_at   = DateTimeCol()
    interval     = IntCol(default=3600)
"""

if __name__ == "__main__":
    import sys
    connection = sqlite3.connect(sys.argv[1])
    Document.create_table()

