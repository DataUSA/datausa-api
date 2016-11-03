import re

from whoosh.qparser import QueryParser
from whoosh import index, sorting, qparser, scoring, query
from config import SEARCH_INDEX_DIR, VAR_INDEX_DIR

class SimpleWeighter(scoring.BM25F):
    use_final = True

    def __init__(self, fullterm, *args, **kwargs):
        self.fullterm = fullterm.lower().strip()
        super(SimpleWeighter, self).__init__(*args, **kwargs)

    def final(self, searcher, docnum, score_me):
        name = searcher.stored_fields(docnum).get("name")
        zvalue = searcher.stored_fields(docnum).get("zvalue")
        zscore = zvalue * .15

        if name == self.fullterm:
            return score_me * 30 + (25 * abs(zscore))
        elif name.startswith(self.fullterm):
            if zvalue > 0:
                return (score_me * 5.75) + (25 * zscore)
            else:
                return score_me * 5.75 + (1 - abs(zscore) * 25)
        elif self.fullterm.startswith(name[:10]):
            return score_me * 3 + abs(zscore)
        elif self.fullterm.startswith(name[:5]):
            return score_me * 1.5 + abs(zscore)
            # return (score_me * 1.75) + (10 * zvalue)
        return (score_me * 0.75) + (zscore * 0.25)


vars_ix = index.open_dir(VAR_INDEX_DIR)
vars_qp = QueryParser("name", schema=vars_ix.schema, group=qparser.OrGroup)


ix = index.open_dir(SEARCH_INDEX_DIR)
qp = QueryParser("name", schema=ix.schema, group=qparser.OrGroup)
facet = sorting.FieldFacet("zvalue", reverse=True)
scores = sorting.ScoreFacet()


def nationwide_results(data, my_vars, attr_score, var_score, usr_query):
    '''given attribute search results and variable search results, determine
    if we should inject the US page into the data'''
    attr_ids = [row[0] for row in data]
    usa = '01000US'
    name = "{} in United States".format(my_vars[0]["description"]) if my_vars else None

    bad_first = data[0][1].lower().startswith(usr_query) if data else True

    if my_vars and var_score and var_score * 17 > attr_score:
        pos = 0 if bad_first else 1
        data.insert(pos, [usa, name, 10, "geo", name, "010", "united-states"])
    elif my_vars and usa not in attr_ids and len(data) < 10:
        data.insert(1, [usa, name, 10, "geo", name, "010", "united-states"])
    return data



def do_search(txt, sumlevel=None, kind=None, tries=0, limit=10, is_stem=None, my_vars=None):
    txt = txt.replace(",", "")

    my_filter = None

    if kind and sumlevel:
        kf = query.Term("kind", kind)
        sf = query.Term("sumlevel", sumlevel)
        my_filter = query.And([kf, sf])
    elif kind:
        my_filter = query.Term("kind", kind)
    elif sumlevel:
        my_filter = query.Term("sumlevel", sumlevel)
    if is_stem and is_stem > 0 and my_filter is not None:
        my_filter = my_filter & query.NumericRange("is_stem", 1, is_stem)
    elif is_stem and is_stem > 0 and my_filter is None:
        my_filter = query.NumericRange("is_stem", 1, is_stem)

    if tries > 2:
        return [], [], [], []
    q = qp.parse(txt)

    var_q = vars_qp.parse(txt)
    var_keywords = {}
    vars_max_score = None
    # search for variables in query
    if not my_vars:
        # my_vars can save original vars detected before autocorrecting for spelling,
        # so we'll only do var searches that haven't yet been autocorrected
        with vars_ix.searcher() as s:
        # s = vars_ix.searcher()
            results = s.search(var_q)
            # raise Exception(list(results)[0])
            vscores = [r.score for r in results]
            vars_max_score = max(vscores) if vscores else None

            my_vars = [{"matched_on": r.highlights("name"),
                        "name": r["name"],
                        "description": r["description"],
                        "section": r["section"],
                        "related_attrs": r["related_attrs"].split(","),
                        "related_vars": r["related_vars"].split(",")} for r in results]
        if my_vars:
            already_seen = []
            filtered_my_vars = []
            for my_var in my_vars:
                if my_var["related_vars"] not in already_seen:
                    filtered_my_vars.append(my_var)
                already_seen.append(my_var["related_vars"])
                highlight_txt = my_var["matched_on"]

                if highlight_txt:
                    matches = re.findall(r'<b class="[^>]+">([^>]+)</b>', highlight_txt)
                    if matches:
                        for matched_txt in matches:
                            var_keywords[matched_txt] = True
            my_vars = filtered_my_vars

    try:
        for term in q:
            for keyword in var_keywords.keys():
                if term.text in keyword:
                    term.boost = -0.1
    except NotImplementedError:
        for keyword in var_keywords.keys():
            if q.text in keyword:
                q.boost = -0.1

    # raise Exception(q)
    weighter = SimpleWeighter(txt, B=.45, content_B=1.0, K1=1.5)
    with ix.searcher(weighting=weighter) as s:
        if len(txt) > 2:
            corrector = s.corrector("display")
            suggs = corrector.suggest(txt, limit=10, maxdist=2, prefix=3)
        else:
            suggs = []
        results = s.search_page(q, 1, sortedby=[scores], pagelen=20, filter=my_filter)
        data = [[r["id"], r["name"], r["zvalue"],
                 r["kind"], r["display"],
                 r["sumlevel"] if "sumlevel" in r else "",
                 r["is_stem"] if "is_stem" in r else False,
                 r["url_name"] if "url_name" in r else None]
                for r in results]

        if not data and suggs:
            return do_search(suggs[0], sumlevel, kind, tries=tries+1, limit=limit, is_stem=is_stem,
                             my_vars=my_vars)

        ascores = [r.score for r in results]
        attr_max_score = max(ascores) if ascores else 0
        # raise Exception(attr_max_score, vars_max_score)
        # insert nationwide linkage
        data = nationwide_results(data, my_vars, attr_max_score, vars_max_score, txt)

        return data, suggs, tries, my_vars
