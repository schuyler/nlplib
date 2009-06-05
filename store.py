from sqlobject import *

class BaseObject (SQLObject):
    _lazyUpdate = True
    _cacheValues = False

class Document (BaseObject):
    title = UnicodeCol(notNull=1)
    description = UnicodeCol(notNull=1)
    url = StringCol(length=255, notNull=1)
    source = StringCol(length=255, notNull=1)
    content_type = StringCol(length=255)
    tags = UnicodeCol(notNull=1)
    vector = BLOBCol()
    revision = IntCol(notNull=1)
    current = BoolCol(notNull=1)
    created_at = TimestampCol(default=None)
    url_idx = DatabaseIndex('url')
    content_type_idx = DatabaseIndex('content_type')
    source_idx = DatabaseIndex('source')

if __name__ == "__main__":
    import sys
    sqlhub.processConnection = connectionForURI("sqlite:" + sys.argv[1])
    Document.createTable()

