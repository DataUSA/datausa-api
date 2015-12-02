'''
Script used to generate the query that makes up the search table
'''

# Industry and Occupation Z-scoring
attrs = [("soc", "pums_1year.yo", "avg_wage", [0, 1, 2, 3]),
         ("naics", "pums_1year.yi", "num_ppl", [0, 1, 2])]

qry = '''SELECT g.{0} as id,  (g.{2} - stats.average) / stats.st AS zvalue, '{0}' as kind , lower(a.name) as name, a.name as display, a.level::text
FROM {1} g 
LEFT JOIN pums_attrs.pums_{0} a ON (a.id = g.{0} and a.level = g.{0}_level)
CROSS JOIN
(select STDDEV({2}) as st, AVG({2}) as average FROM {1} WHERE {0}_level={3} AND year=2013) stats
WHERE g.{0}_level = {3}
AND g.year = 2013'''

queries = []
for attr, table, metric, levels in attrs:
    for level in levels:
        queries.append(qry.format(attr, table, metric, level))
        #print queries[0]



# CIP codes
cip_qry = '''SELECT g.{0},  (g.{2} - stats.average) / stats.st AS zvalue, '{0}' as kind , lower(a.name) as name, a.name as display, a.level::text
FROM {1} g 
LEFT JOIN attrs.course a ON (a.id = g.{0})
CROSS JOIN
(select STDDEV({2}) as st, AVG({2}) as average FROM {1} WHERE char_length({0}) = {3} AND year=2013) stats
WHERE char_length({0}) = {3}
AND g.year = 2013'''

for level in [2, 4, 6]:
    queries.append(cip_qry.format("cip", "ipeds_beta.grads_yc", "grads_total", level))

# GEO codes
geo_qry = '''SELECT g.{0},  (g.{2} - stats.average) / stats.st AS zvalue, '{0}' as kind , lower(a.name) as name, a.display_name as display, a.sumlevel::text as level
FROM {1} g 
LEFT JOIN attrs.geo_names a ON (a.id = g.{0})
CROSS JOIN
(select STDDEV({2}) as st, AVG({2}) as average FROM {1} WHERE {0} LIKE '{3}%' AND year=2013) stats
WHERE g.{0} LIKE '{3}%'
AND g.year = 2013'''

for level in ['040', '050', '160', '310', '795']:
    queries.append(geo_qry.format("geo", "acs.yg", "pop", level))

queries.append("SELECT '01000US', 150, 'geo', 'united states', 'United States', '010'")

tail_qrys = ["({})".format(q) if i!= 0 else q for i,q in enumerate(queries)]
final_q = "\n UNION \n".join(tail_qrys);
print final_q
