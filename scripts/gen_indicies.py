'''
Script used to add indexes for PUMS tables
'''
import itertools

lookup = {
    "a": "age",
    "b": "birthplace",
    "c": "cip",
    "d": "degree",
    "s": "sector",
    "g": "geo",
    "i": "naics",
    "o": "soc",
    "r": "race",
    "s": "sex",
    "w": "wage_bin",
    "y": "year",
}

tables = [
    'ya',
    'yc',
    'yca',
    'ycb',
    'ycd',
    'ycs',
    'yg',
    'ygb',
    'ygc',
    'ygd',
    'ygi',
    'ygio',
    'ygo',
    'ygor',
    'ygos',
    'ygr',
    'ygs',
    'ygw',
    'yi',
    'yic',
    'yid',
    'yio',
    'yior',
    'yios',
    'yir',
    'yis',
    'yiw',
    'yo',
    'yoas',
    'yoc',
    'yocd',
    'yod',
    'yor',
    'yos',
    'yow',
]
schema = 'pums_1yr'

def has_prefix(indexes, index):
    for ix in indexes:
        if ix.startswith(index):
            return True
    return False

def gen_index(table, idx_id, is_pk=False):
    cols = [lookup[l] for l in idx_id]
    if is_pk:
        if "i" in table:
            cols.append("naics_level")
        if "o" in table:
            cols.append("soc_level")
    cols = ",".join(cols)
    unq = "" if not is_pk else "UNIQUE"
    qry = "CREATE {4} INDEX {1}_{2}_idx ON {0}.{1} ({3});".format(schema, table, idx_id, cols, unq)
    return qry

for table in tables:
    indexes = []
    sizes = range(1, len(table) + 1)
    sizes.reverse()
    for size in sizes:
        tmp = list(itertools.combinations(table, size))
        indexes += [''.join(x) for x in tmp if not has_prefix(indexes, ''.join(x))]

    # indexes to create
    for index in indexes:
        print gen_index(table, index, len(index) == len(table))
