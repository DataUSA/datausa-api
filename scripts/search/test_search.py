from whoosh.qparser import QueryParser
from whoosh import index
from whoosh import qparser
from config import SEARCH_INDEX_DIR

ix = index.open_dir(SEARCH_INDEX_DIR)
qp = QueryParser("name", schema=ix.schema, group=qparser.OrGroup)


def whoosh_search(txt):
    q = qp.parse(txt)
    with ix.searcher() as s:
        results = s.search(q)
        data = [[r["id"], r["name"], r["zvalue"],
                 r["kind"], r["display"], r["sumlevel"]]
                for r in results]
        data.sort(key=lambda x: x[2], reverse=True)  # sort by zvalue
        return data

if __name__ == '__main__':
    txt = "new york econ"
    print whoosh_search(txt)
