SELECT
    '86000US' || zcta5.geoid10 AS child_geoid,
    '31000US' || cbsa.geoid AS parent_geoid,
    ST_Area(ST_Intersection(zcta5.geom,cbsa.geom))/ST_Area(zcta5.geom)*100 as percent_covered, 
    ST_Area(cbsa.geom) as parent_area
FROM tiger2013.zcta5
JOIN tiger2013.cbsa ON ST_Intersects(zcta5.geom, cbsa.geom)
WHERE
    ST_Area(ST_Intersection(zcta5.geom,cbsa.geom))/ST_Area(zcta5.geom) > 0
UNION
(SELECT
    '86000US' || zcta5.geoid10 AS child_geoid,
    '16000US' || place.geoid AS parent_geoid,
    ST_Area(ST_Intersection(zcta5.geom,place.geom))/ST_Area(zcta5.geom)*100 as percent_covered, 
    ST_Area(place.geom) as parent_area
FROM tiger2013.zcta5
JOIN tiger2013.place ON ST_Intersects(zcta5.geom, place.geom)
WHERE
    ST_Area(ST_Intersection(zcta5.geom,place.geom))/ST_Area(zcta5.geom) > 0
and ST_IsValid(zcta5.geom))
UNION
(SELECT
    '86000US' || zcta5.geoid10 AS child_geoid,
    '05000US' || county.geoid AS parent_geoid,
    ST_Area(ST_Intersection(zcta5.geom,county.geom))/ST_Area(zcta5.geom)*100 as percent_covered, 
    ST_Area(county.geom) as parent_area
FROM tiger2013.zcta5
JOIN tiger2013.county ON ST_Intersects(zcta5.geom, county.geom)
WHERE
    ST_Area(ST_Intersection(zcta5.geom, county.geom))/ST_Area(zcta5.geom) > 0
and ST_IsValid(zcta5.geom))
UNION
(SELECT
    '86000US' || zcta5.geoid10 AS child_geoid,
    '79500US' || puma.geoid10 AS parent_geoid,
    ST_Area(ST_Intersection(zcta5.geom,puma.geom))/ST_Area(zcta5.geom)*100 as percent_covered, 
    ST_Area(puma.geom) as parent_area
FROM tiger2013.zcta5
JOIN tiger2013.puma ON ST_Intersects(zcta5.geom, puma.geom)
WHERE
    ST_Area(ST_Intersection(zcta5.geom, puma.geom))/ST_Area(zcta5.geom) > 0
and ST_IsValid(zcta5.geom))