'''
Script used to generate the query that makes up the search table
'''
from datausa.pums.abstract_models import BasePums

pums_schema_name = BasePums.get_schema_name()

# Industry and Occupation Z-scoring
attrs = [("soc", "{}.yo".format(pums_schema_name), "avg_wage", [0, 1, 2, 3]),
         ("naics", "{}.yi".format(pums_schema_name), "num_ppl", [0, 1, 2])]

qry = '''SELECT g.{0} as id,  (g.{2} - stats.average) / stats.st AS zvalue, '{0}' as kind , lower(a.name) as name, a.name as display, a.level::text as sumlevel, -1 as is_stem, a.url_name as url_name, a.keywords as keywords
FROM {1} g
LEFT JOIN pums_attrs.pums_{0} a ON (a.id = g.{0} and a.level = g.{0}_level)
CROSS JOIN
(select STDDEV({2}) as st, AVG({2}) as average FROM {1} WHERE {0}_level={3} AND year=2015) stats
WHERE g.{0}_level = {3}
AND g.year = 2015'''

queries = []
for attr, table, metric, levels in attrs:
    for level in levels:
        queries.append(qry.format(attr, table, metric, level))
        #print queries[0]



# CIP codes
cip_qry = '''SELECT g.{0},  (g.{2} - stats.average) / stats.st AS zvalue, '{0}' as kind , lower(a.name) as name, a.name as display, a.level::text as sumlevel, a.is_stem as is_stem, a.url_name as url_name, a.keywords as keywords
FROM {1} g
LEFT JOIN attrs.course a ON (a.id = g.{0})
CROSS JOIN
(select STDDEV({2}) as st, AVG({2}) as average FROM {1} WHERE char_length({0}) = {3} AND year=2015) stats
WHERE char_length({0}) = {3}
AND g.year = 2015'''

for level in [2, 4, 6]:
    queries.append(cip_qry.format("cip", "ipeds.grads_yc", "grads_total", level))

# GEO codes
geo_qry = '''SELECT g.{0},  (g.{2} - stats.average) / stats.st AS zvalue, '{0}' as kind , lower(a.name) as name, a.display_name as display, a.sumlevel::text as sumlevel, -1 as is_stem, a.url_name as url_name, a.keywords as keywords
FROM {1} g
LEFT JOIN attrs.geo_names a ON (a.id = g.{0})
CROSS JOIN
(select STDDEV({2}) as st, AVG({2}) as average FROM {1} WHERE {0} LIKE '{3}%' AND year=2015) stats
WHERE g.{0} LIKE '{3}%'
AND g.year = 2015'''

for level in ['040', '050', '160', '310', '795']:
    queries.append(geo_qry.format("geo", "acs_5yr.yg", "pop", level))

queries.append("SELECT '01000US', 150, 'geo', 'united states', 'United States', '010', -1, 'united-states', '{usa, us, america}'")


# UNIVERSITIES
university_qry = '''SELECT g.{0},  (g.{2} - stats.average) / stats.st AS zvalue, '{0}' as kind , lower(a.name) as name, a.display_name as display, a.university_level::text as sumlevel, a.is_stem as is_stem, a.url_name as url_name, a.keywords as keywords
                    FROM {1} g
                    LEFT JOIN attrs.university a ON (a.id = g.{0})
                    CROSS JOIN
                        (select STDDEV({2}) as st, AVG({2}) as average FROM {1} WHERE year=2015) stats
                        WHERE g.year = 2015 and a.status != 'D' '''

queries.append(university_qry.format("university", "ipeds.grads_yu", "grads_total"))

tail_qrys = ["({})".format(q) if i != 0 else q for i, q in enumerate(queries)]
final_q = "\n UNION \n".join(tail_qrys)
print(final_q)
