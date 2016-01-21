GEO = 'geo'
PUMA = 'puma'
MSA = 'msa'
COUNTY = 'county'
STATE = 'state'
NATION = 'nation'
MSA = 'msa'
TRACT = 'tract'
PLACE = 'place'
PUMA = 'puma'

ALL = 'all'
OR = ","
YEAR = 'year'
LATEST = 'latest'
OLDEST = 'oldest'
GEO_LEVEL_MAP = {NATION: "010", STATE: "040", COUNTY: "050",
                 PUMA: "795", MSA: "310", PLACE: "160", TRACT: "140"}
LEVEL_TO_GEO = {v: k for k,v in GEO_LEVEL_MAP.items()}

POP_THRESHOLD = 250000
NO_VALUE_ADDED = 'no_value_added'
