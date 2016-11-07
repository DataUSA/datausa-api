import os
import os.path
import json

from whoosh import index
from whoosh.fields import Schema, TEXT, NGRAMWORDS
from config import VAR_INDEX_DIR


def get_schema():
    return Schema(related_vars=TEXT(stored=True),
                  name=NGRAMWORDS(stored=True, minsize=3, maxsize=12, at='start', queryor=True),
                  description=TEXT(stored=True),
                  section=TEXT(stored=True),
                  related_attrs=TEXT(stored=True),
                  params=TEXT(stored=True))

if __name__ == '__main__':
    print("Building index...")
    if not os.path.exists(VAR_INDEX_DIR):
        os.mkdir(VAR_INDEX_DIR)
        ix = index.create_in(VAR_INDEX_DIR, get_schema())
        print("Creating variables index...")

    ix = index.open_dir(VAR_INDEX_DIR)
    writer = ix.writer()

    all_vars = [
        [u'adult_obesity,diabetes', u'obesity', u'Obesity prevalence', u'obesity_diabetes', u'geo', None],
        [u'adult_obesity,diabetes', u'diabetes', u'Diabetes prevalence', u'obesity_diabetes', u'geo', None],
        [u'adult_obesity,diabetes', u'healthcare', u'Healthcare', u'obesity_diabetes', u'geo', None],
        [u'motor_vehicle_crash_deaths', u'car crashes', u'Motor vehicle crash deaths', u'crime', u'geo', None],
        [u'adult_smoking', u'smokers', u'Percentage of adults that reported smoking', u'substance_abuse', u'geo', None],

        # [u'infant_mortality', u'infant mortality', u'Infant mortality', u'health', u'geo'],
        # [u'teen_births', u'teen births', u'Teen births', u'health', u'geo'],
        [u'mean_commute_minutes', u'commuters', u'Average travel time', u'commute_time', u'geo', None],
        [u'mean_commute_minutes', u'transit', u'Average travel time', u'commute_time', u'geo', None],
        [u'mean_commute_minutes', u'transportation', u'Average travel time', u'commute_time', u'geo', None],
        [u'mean_commute_minutes', u'travel time', u'Average travel time', u'commute_time', u'geo', None],

        [u'conflict_total', u'veterans', u'Number of veterans', u'veterans', u'geo', None],
        [u'crime', u'crime', u'Crime', u'crime', u'geo', None],
        [u'murder', u'murder', u'Murder', u'crime', u'geo', None],
        [u'pop,age', u'population', u'Population', u'demographics', u'geo', None],
        [u'pop,age', u'people', u'Population', u'demographics', u'geo', None],
        [u'age', u'age', u'Median Age', u'demographics', u'geo', None],
        [u'income', u'income', u'Median income', u'economy', u'geo', None],
        [u'avg_wage', u'salary', u'Average wage', u'economy', u'geo', None],
        [u'avg_wage', u'wage', u'Average wage', u'economy', u'geo', None],
        [u'income,age,pop', u'economy', u'Economic data', u'economy', u'geo', None],
        [u'avg_wage', u'wages', u'Wages', u'income_distro', u'geo', None],
        [u'median_property_value', u'property value', u'Property values', u'economy', u'geo', None],
        [u'income_below_poverty', u'poverty', u'Poverty', u'poverty_age_gender', u'geo', None],
        [u'households_renter_occupied,households_owner_occupied,households', u'renters', u'Renter occupied households', u'rent_own', u'geo', None],
        [u'grads_total', u'graduates', u'Postsecondary degree graduates', u'education', u'geo', None],
        [u'grads_total', u'grads', u'Postsecondary degree graduates', u'education', u'geo', None],
    ]
    from datausa.attrs.models import AcsLanguage

    for lang in AcsLanguage.query.all():
        my_params = {
            "year": "latest",
            "language": lang.id
        }
        my_var = [u'num_speakers', u'{}'.format(lang.name.lower()),
                  u'{} Speakers'.format(lang.name), u'languages', u'geo', unicode(json.dumps(my_params))]
        print my_var
        all_vars.append(my_var)


    for related_vars, name, description, section, related_attrs, params in all_vars:
        writer.add_document(related_vars=related_vars, name=name,
                            description=description, section=section,
                            related_attrs=related_attrs, params=params)
    writer.commit()
