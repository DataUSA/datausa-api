'''Logic for handling parsing of variables in search queries'''
import regex
from fuzzywuzzy import process

from datausa.attrs.models import AcsLanguage, Cip, PumsSoc, PumsBirthplace

# TODO cache
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
    results = []
    final_txt = txt

    in_split = final_txt.split(" in ", 1)
    has_in = len(in_split) > 1
    for my_var in vars_list:
        tmp_result = {
            "required": my_var,
            "year": "latest",
            "sumlevel": "all"
        }

        in_split[0] = regex.sub(r"(" + my_var + r"){e<=3}\w*", "",
                                in_split[0]).strip()

        # if best_attr_names:
                # tmp_result[best_subvarname] = best_attr_names[0]
        results.append(tmp_result)

    if has_in:
        final_txt = in_split[-1].strip()

    final_txt = regex.sub(r"^\s*(of\s*in|of|in\s*) ", "", final_txt).strip()
    return {"vars" : results, "query": final_txt}

def var_search(txt):
    '''Takes a query and returns a list of related variables'''

    var_list = {
        "age": ["age"],
        "people": ["pop", "age"],
        "population": ["pop", "age"],
        "income": ["income"],
        "economy": ["income", "avg_wage", "num_ppl"],
        "salary": ["avg_wage"],
        "diabetes": ["diabetes", "adult_obesity"],
        "obesity": ["adult_obesity", "diabetes"],
        "healthcare": ["uninsured", "diabetes"],
        # "speakers": ["num_speakers"],
        "graduates": ["grads_total"],
        "car crash": ["motor_vehicle_crash_deaths"],
        "infant_mortality": ["infant_mortality"],
        "crime": ["violent_crime"],
        "murder": ["homicide_rate"],
        "teen births": ["teen_births"],
        "property value": ["median_property_value"]
    }

    results = process.extract(txt, var_list.keys())
    var_names = [item for keyword, score in results if score >= 75
                 for item in var_list[keyword]]

    # if not var_names and " in " in txt:
        # var_names = ["num_ppl"]

    for matched_keyword, _ in results:
        txt = txt.replace(matched_keyword, "").strip()

    return var_support_map(txt, var_names)

# def var_support_map(txt, vars_list):
#     '''given a list of variables return a mapping of variables supported by attr'''
#
#     two_pass_list = {
#         "num_speakers": [{"mapper": build_attr_map(AcsLanguage), "name": "language"}],
#         "grads_total": [{"mapper": build_attr_map(Cip), "name": "cip"}],
#         "num_ppl": [{"mapper": build_attr_map(PumsBirthplace, "denonym",
#                                              [~PumsBirthplace.id.like("XX%")]),
#                     "name": "birthplace"},
#                     {"mapper": build_attr_map(PumsSoc), "name": "soc"}],
#     }
#
#     results = []
#     final_txt = txt
#
#     in_split = final_txt.split(" in ")
#     has_in = len(in_split) > 1
#     for my_var in vars_list:
#         tmp_result = {
#             "required": my_var,
#             "sumlevel": "all",
#             "year": "latest"
#         }
#         if my_var in two_pass_list:
#             best_high_score = 0
#             best_match = None
#             best_attr_names = None
#             best_subvarname = None
#             for mapper_obj in two_pass_list[my_var]:
#                 # mapper_obj = two_pass_list[my_var]
#                 mapper = mapper_obj["mapper"]
#                 subvarname = mapper_obj["name"]
#                 attr_results = process.extract(txt if not has_in else in_split[0], mapper.keys())
#                 # raise Exception(attr_results)
#                 attr_names = [mapper[keyword] for keyword, score in attr_results if score >= 90]
#                 high_score = max([score for _, score in attr_results])
#                 # raise Exception(high_score)
#                 if high_score >= best_high_score:
#                     best_high_score = high_score
#                     best_match = attr_results[0][0]
#                     best_high_score = high_score
#                     best_attr_names = attr_names
#                     best_subvarname  =subvarname
#
#             # raise Exception(best_match, best_high_score)
#             if not has_in:
#                 final_txt = final_txt.replace(best_match, "").strip()
#             else:
#                 # use regex to eliminate the reset of the matched word
#                 in_split[0] = regex.sub(r"(" + best_match + r"){e<=3}\w*", "",
#                                         in_split[0]).strip()
#
#             if best_attr_names:
#                 tmp_result[best_subvarname] = best_attr_names[0]
#         results.append(tmp_result)
#
#
#     if has_in:
#         in_split = [word.strip() for word in in_split]
#         final_txt = " in ".join(in_split)
#
#     final_txt = regex.sub(r"^\s*(of\s*in|of|in\s*) ", "", final_txt).strip()
#     return {"vars" : results, "query": final_txt}
