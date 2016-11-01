import os
import os.path

from whoosh import index
from whoosh.fields import Schema, TEXT, NGRAMWORDS
from config import VAR_INDEX_DIR

def get_schema():
    return Schema(related_vars=TEXT(stored=True),
                  name=NGRAMWORDS(stored=True, minsize=3, maxsize=12, at='start', queryor=True),
                  description=TEXT(stored=True),
                  section=TEXT(stored=True),
                  related_attrs=TEXT(stored=True))

if __name__ == '__main__':
    print("Building index...")
    if not os.path.exists(VAR_INDEX_DIR):
        os.mkdir(VAR_INDEX_DIR)
        ix = index.create_in(VAR_INDEX_DIR, get_schema())
        print("Creating variables index...")

    ix = index.open_dir(VAR_INDEX_DIR)
    writer = ix.writer()

    all_vars = [
        [u'adult_obesity,diabetes', u'obesity', u'Obesity prevalence', u'obesity_diabetes', u'geo'],
        [u'adult_obesity,diabetes', u'diabetes', u'Diabetes prevalence', u'obesity_diabetes', u'geo'],
        [u'adult_obesity,diabetes', u'healthcare', u'Healthcare', u'obesity_diabetes', u'geo'],
        [u'motor_vehicle_crash_deaths', u'car crashes', u'Motor vehicle crash deaths', u'crime', u'geo'],
        [u'adult_smoking', u'smokers', u'Percentage of adults that reported smoking', u'substance_abuse', u'geo'],

        # [u'infant_mortality', u'infant mortality', u'Infant mortality', u'health', u'geo'],
        # [u'teen_births', u'teen births', u'Teen births', u'health', u'geo'],
        [u'mean_commute_minutes', u'commuters', u'Average travel time', u'commute_time', u'geo'],
        [u'mean_commute_minutes', u'transit', u'Average travel time', u'commute_time', u'geo'],
        [u'mean_commute_minutes', u'transportation', u'Average travel time', u'commute_time', u'geo'],

        [u'conflict_total', u'veterans', u'Number of veterans', u'veterans', u'geo'],
        [u'crime', u'crime', u'Crime', u'crime', u'geo'],
        [u'murder', u'murder', u'Murder', u'crime', u'geo'],
        [u'pop,age', u'population', u'Population', u'demographics', u'geo'],
        [u'pop,age', u'people', u'Population', u'demographics', u'geo'],
        [u'age', u'age', u'Median Age', u'demographics', u'geo'],
        [u'income', u'income', u'Median income', u'economy', u'geo'],
        [u'avg_wage', u'salary', u'Average wage', u'economy', u'geo'],
        [u'avg_wage', u'wage', u'Average wage', u'economy', u'geo'],
        [u'income,age,pop', u'economy', u'Economic data', u'economy', u'geo'],
        [u'avg_wage', u'wages', u'Wages', u'income_distro', u'geo'],
        [u'median_property_value', u'property value', u'Property values', u'economy', u'geo'],
        [u'income_below_poverty', u'poverty', u'Poverty', u'poverty_age_gender', u'geo'],
        [u'households_renter_occupied,households_owner_occupied,households', u'renters', u'Renter occupied households', u'rent_own', u'geo'],

    ]

    for related_vars, name, description, section, related_attrs in all_vars:
        writer.add_document(related_vars=related_vars, name=name,
                            description=description, section=section,
                            related_attrs=related_attrs)
    writer.commit()
