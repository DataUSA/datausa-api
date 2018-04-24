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
                  section_title=TEXT(stored=True),
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
        [u'adult_obesity,diabetes', u'obesity', u'Obesity Prevalence,Diabetes Prevalence', u'conditions_diseases', u'Healthcare', u'geo', None],
        [u'adult_obesity,diabetes', u'diabetes', u'Obesity Prevalence,Diabetes Prevalence', u'conditions_diseases', u'Healthcare',  u'geo', None],
        [u'adult_obesity,diabetes', u'healthcare', u'Obesity Prevalence,Diabetes Prevalence', u'conditions_diseases', u'Healthcare', u'geo', None],
        [u'motor_vehicle_crash_deaths', u'car crashes', u'Motor Vehicle Crash Deaths', u'risky', u'Crime', u'geo', None],
        [u'motor_vehicle_crash_deaths', u'accidents', u'Motor Vehicle Crash Deaths', u'risky', u'Crime', u'geo', None],

        [u'adult_smoking', u'smokers', u'Adult Smoking Prevalence', u'risky', u'Healthcare', u'geo', None],
        [u'adult_smoking', u'cigarettes', u'Adult Smoking Prevalence', u'risky', u'Healthcare', u'geo', None],

        # [u'infant_mortality', u'infant mortality', u'Infant mortality', u'health', u'geo'],
        # [u'teen_births', u'teen births', u'Teen births', u'health', u'geo'],
        [u'mean_commute_minutes', u'commuters', u'Average Travel Time', u'commute_time', u'Transportation', u'geo', None],
        [u'mean_commute_minutes', u'transit', u'Average Travel Time', u'commute_time', u'Transportation', u'geo', None],
        [u'mean_commute_minutes', u'transportation', u'Average Travel Time', u'commute_time', u'Transportation', u'geo', None],
        [u'mean_commute_minutes', u'travel time', u'Average Travel Time', u'commute_time', u'Transportation', u'geo', None],

        [u'conflict_total', u'veterans', u'Number of Veterans', u'veterans', u'Military', u'geo', None],
        [u'conflict_total', u'war', u'Number of Veterans', u'veterans', u'Military', u'geo', None],

        [u'violent_crime', u'crime', u'Violent Crimes', u'crime', u'Crime', u'geo', None],
        [u'homicide_rate', u'murder', u'Homicide Deaths', u'crime', u'Crime', u'geo', None],
        [u'homicide_rate', u'homicide', u'Homicide Deaths', u'crime', u'Crime', u'geo', None],

        [u'pop,age', u'population', u'Population,Median Age', u'demographics', u'Demographics', u'geo', None],
        [u'pop,age', u'people', u'Population,Median Age', u'demographics', u'Demographics', u'geo', None],
        [u'age', u'age', u'Median Age', u'demographics', u'Demographics', u'geo', None],
        [u'income', u'income', u'Median Yearly Income', u'economy', u'Economy', u'geo', None],
        [u'avg_wage', u'salaries', u'Average Salary', u'economy', u'Economy', u'geo,soc,naics,cip', None],
        [u'avg_wage', u'wage', u'Average Salary', u'economy', u'Economy', u'geo,soc,naics,cip', None],
        [u'income,age,pop', u'economics', u'Median Yearly Income,Age,Population', u'economy', u'Economy', u'geo', None],
        # [u'avg_wage', u'wages', u'Wages', u'income_distro', u'geo', None],
        [u'median_property_value', u'property value', u'Median Property Value', u'economy', u'Economy', u'geo', None],
        [u'median_property_value', u'home value', u'Median Property Value', u'economy', u'Economy', u'geo', None],
        [u'median_property_value', u'housing cost', u'Median Property Value', u'economy', u'Economy', u'geo', None],

        [u'income_below_poverty', u'poverti', u'Population in Poverty', u'poverty_age_gender', u'Wages', u'geo', None],
        [u'income_below_poverty', u'poor', u'Population in Poverty', u'poverty_age_gender', u'Wages', u'geo', None],

        [u'households_renter_occupied,households_owner_occupied,households', u'renters', u'Renter occupied households', u'rent_own', u'Housing', u'geo', None],
        [u'grads_total', u'graduates', u'Degrees Awarded', u'education', u'Housing', u'geo', None],
        [u'grads_total', u'grads', u'Degrees Awarded', u'education', u'Housing', u'geo', None],
        [u'grads_total', u'students', u'Degrees Awarded', u'education', u'Housing', u'geo', None],

        [u'nativity_foreign,nativity_us', u'foreign born', u'Foreign Born,Native Born', u'demographics', u'Demographics', u'geo', None],
        [u'nativity_foreign,nativity_us', u'native born', u'Foreign Born,Native Born', u'demographics', u'Demographics', u'geo', None],

        [u'pop_black,pop_latino,pop_white,pop_asian', u'race ethnicity', u'Black Population,Hispanic Population,White Population,Asian Population', u'ethnicity', u'Heritage', u'geo', None],
        [u'us_citizens', u'citizen', u'Citizenship', u'citizenship', u'Heritage', u'geo', None],
        [u'gini', u'gini', u'Gini', u'income_distro', u'Wages', u'geo', None],
        [u'gini', u'inequality', u'Gini', u'income_distro', u'Wages', u'geo', None],
        [u'pop_latino', u'hispanic', u'Hispanic Population', u'ethnicity', u'Heritage', u'geo', None],
        [u'pop_latino', u'latino', u'Hispanic Population', u'ethnicity',  u'Heritage', u'geo', None],
        [u'pop_black', u'black', u'Black Population', u'ethnicity',  u'Heritage', u'geo', None],
        [u'pop_white', u'white', u'White Population', u'ethnicity',  u'Heritage', u'geo', None],
        [u'pop_asian', u'asian', u'Asian Population', u'ethnicity',  u'Heritage', u'geo', None],
        [u'transport_bicycle', u'bicycle', u'Bicycle to Work', u'mode_transport', u'Transportation', u'geo', None],
        [u'transport_bicycle', u'bikers', u'Bicycle to Work', u'mode_transport', u'Transportation', u'geo', None],
        [u'transport_bicycle', u'cyclist', u'Bicycle to Work', u'mode_transport', u'Transportation', u'geo', None],
        [u'transport_carpooled', u'carpool', u'Carpool to Work', u'mode_transport', u'Transportation', u'geo', None],
        [u'transport_publictrans', u'public transit', u'Public Transit to Work', u'mode_transport', u'Transportation', u'geo', None],
        [u'transport_drove', u'drive', u'Drove Alone to Work', u'mode_transport', u'Transportation', u'geo', None],
        [u'transport_drove', u'cars', u'Drove Alone to Work', u'mode_transport', u'Transportation', u'geo', None],
        [u'transport_drove', u'drivers', u'Drove Alone to Work', u'mode_transport', u'Transportation', u'geo', None],
        [u'transport_taxi', u'taxi', u'Taxi to Work', u'mode_transport', u'Transportation', u'geo', None],
        [u'transport_motorcycle', u'motorcycle', u'Motorcycled to Work', u'mode_transport', u'Transportation', u'geo', None],
        [u'transport_walked', u'walk', u'Walked to Work', u'mode_transport', u'Transportation', u'geo', None],

    ]

    from datausa.attrs.models import AcsLanguage, PumsBirthplace

    for lang in AcsLanguage.query.all():
        my_params = {
            "year": "latest",
            "language": lang.id
        }
        my_var = [u'num_speakers', u'{}'.format(lang.name.lower()),
                  u'{} Speakers'.format(lang.name), u'languages', u'Heritage', u'geo', unicode(json.dumps(my_params))]
        print my_var
        all_vars.append(my_var)


    for birthplace in PumsBirthplace.query.filter(~PumsBirthplace.id.startswith("XX"),
                                            ~PumsBirthplace.id.startswith("040")):
        if birthplace.id in ["161", "344"]: # skip georgia and car
            continue
        my_params = {
            "year": "latest",
            "birthplace": birthplace.id
        }
        b_keyword = birthplace.demonym or birthplace.name
        b_keyword = b_keyword.lower().strip()
        b_keyword = " ".join([k for k in b_keyword.split(" ") if len(k) > 3])
        my_var = [u'num_over5', u'{}'.format(b_keyword),
                  u'People Born in {}'.format(birthplace.name.title()), u'heritage', u'Heritage', u'geo', unicode(json.dumps(my_params))]
        print my_var
        all_vars.append(my_var)

    for related_vars, name, description, section, section_title, related_attrs, params in all_vars:
        # print '|{}|{}|{}|'.format(name, description, related_vars)
        writer.add_document(related_vars=related_vars, name=name,
                            description=description, section=section,
                            section_title=section_title,
                            related_attrs=related_attrs, params=params)
    writer.commit()
