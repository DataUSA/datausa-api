'''Logic for handling parsing of variables in search queries'''
import regex
from fuzzywuzzy import process

from datausa import cache

from datausa.attrs.models import Search
from datausa.core.models import VariableManager, Variable

@cache.memoize()
def build_attr_map(attr_obj, key=None, filters=None):
    '''Given an attribute object return a mapping dictionary of names to IDs'''
    ents = [attr_obj.id, attr_obj.name]
    if key:
        ents.append(getattr(attr_obj, key))

    qry = attr_obj.query.with_entities(*ents)

    if filters:
        qry = qry.filter(*filters)

    return {(getattr(x, key) or x.name if key else x.name).lower(): x.id
            for x in qry}

def var_support_map(txt, vars_list):
    '''given a list of variables return a mapping of variables supported by attr'''
    final_txt = txt
    in_split = final_txt.split(" in ", 1)
    has_in = len(in_split) > 1
    results = []

    for my_var in vars_list:
        in_split[0] = regex.sub(r"(" + my_var.keyword + r"){e<=3}\w*", "",
                                in_split[0]).strip()
        results.append(my_var)

    if has_in:
        final_txt = in_split[-1].strip()

    if not has_in:
        entities = build_attr_map(Search).keys()
        entities = [ent.replace("," ,"") for ent in entities]
        candidates = [attr_name for attr_name in entities if attr_name in final_txt and len(attr_name) > 2]
        matched_attrs = sorted(candidates, key=len, reverse=True)

        if matched_attrs:
            final_txt = matched_attrs[0]

    final_txt = regex.sub(r"^\s*(of\s*in|of|in\s*) ", "", final_txt).strip()
    return {"vars" : results, "query": final_txt, "matched": vars_list}

def var_search(txt):
    '''Takes a query and returns a list of related variables'''

    var_manager = VariableManager([
        Variable("age", ["age"]),
        Variable("people", ["pop", "age"]),
        Variable("population", ["pop", "age"]),
        Variable("income", ["income"]),
        Variable("economy", ["income", "age", "pop"]),
        Variable("salary", ["avg_wage"]),
        Variable("diabetes", ["diabetes", "adult_obesity"]),
        Variable("obesity", ["adult_obesity", "diabetes"]),
        Variable("healthcare", ["uninsured", "diabetes"]),
        Variable("graduates", ["grads_total"]),
        Variable("car crashes", ["motor_vehicle_crash_deaths"]),
        Variable("infant mortality", ["infant_mortality"]),
        Variable("crime", ["violent_crime"]),
        Variable("murder", ["homicide_rate"]),
        Variable("teen births", ["teen_births"]),
        Variable("property value", ["median_property_value"])
    ])


    var_results = process.extract(txt, var_manager.keywords())

    var_names = [var_manager.lookup(keyword) for keyword, score in var_results if score >= 90]
    # raise Exception(var_names)
    # if there are no fuzzy matches but the query is a prefix of one of the variables
    # include that variable
    if not var_names:
        var_names = [var_name for var_name in var_names if var_name.startswith(txt)]

    return var_support_map(txt, var_names)
