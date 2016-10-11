'''Logic for handling parsing of variables in search queries'''
import regex
from fuzzywuzzy import process
from datausa.attrs.models import AcsLanguage, Cip, Soc

# TODO cache
def build_attr_map(attr_obj):
    '''Given an attribute object return a mapping dictionary of names to IDs'''
    return {x.name.lower(): x.id for x in attr_obj.query.with_entities(attr_obj.id, attr_obj.name)}

def var_support_map(txt, vars_list):
    '''given a list of variables return a mapping of variables supported by attr'''

    two_pass_list = {
        "num_speakers": {"mapper": build_attr_map(AcsLanguage), "name": "language"},
        "grads_total": {"mapper": build_attr_map(Cip), "name": "cip"},
        "num_ppl": {"mapper": build_attr_map(Soc), "name": "soc"},
    }

    results = []
    final_txt = txt

    in_split = final_txt.split(" in ")
    has_in = len(in_split) > 1
    for my_var in vars_list:
        tmp_result = {
            "required": my_var,
            "sumlevel": "all",
            "year": "latest"
        }
        if my_var in two_pass_list:
            mapper = two_pass_list[my_var]["mapper"]
            subvarname = two_pass_list[my_var]["name"]
            attr_results = process.extract(txt if not has_in else in_split[0], mapper.keys())
            # raise Exception(attr_results)
            attr_names = [mapper[keyword] for keyword, score in attr_results if score >= 90]
            # raise Exception(results)
            for matched_attr_key, _ in attr_results:
                if not has_in:
                    final_txt = final_txt.replace(matched_attr_key, "").strip()
                else:
                    # use regex to eliminate the reset of the matched word
                    in_split[0] = regex.sub(r"(" + matched_attr_key + r"){e<=3}\w*", "",
                                            in_split[0]).strip()

            if attr_names:
                tmp_result[subvarname] = attr_names[0]
        results.append(tmp_result)


    if has_in:
        in_split = [word.strip() for word in in_split]
        final_txt = " in ".join(in_split)

    final_txt = regex.sub(r"^\s*(of\s*in|of|in\s*) ", "", final_txt).strip()
    return {"vars" : results, "query": final_txt}

def var_search(txt):
    '''Takes a query and returns a list of related variables'''

    var_list = {
        "income": ["income"],
        "population": ["pop"],
        "economy": ["income", "avg_wage"],
        "diabetes": ["diabetes", "adult_obesity"],
        "obesity": ["adult_obesity", "diabetes"],
        "healthcare": ["uninsured", "diabetes"],
        "speakers": ["num_speakers"],
        "graduates": ["grads_total"]
    }

    results = process.extract(txt, var_list.keys())
    var_names = [item for keyword, score in results if score >= 90
                 for item in var_list[keyword]]

    if not var_names and " in " in txt:
        var_names = ["num_ppl", "avg_age"]

    for matched_keyword, _ in results:
        txt = txt.replace(matched_keyword, "").strip()

    return var_support_map(txt, var_names)
