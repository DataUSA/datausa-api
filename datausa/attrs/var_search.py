from fuzzywuzzy import process

def var_search(txt):
    '''Takes a query and returns a modified version of the query and
    a list of related variables'''
    var_list = {
        "population": "pop",
        "people": "pop",
        "age": "age",
        "income": "income",
        "earnings": "income",
        "wage": "avg_wage",
        "salary": "avg_wage",
        "veterans": "conflict_total",
        "poverty": "income_below_poverty",
        "poor": "income_below_poverty",
        "supercommuters": "travel_90over",
        "number": "num_ppl",
        "obesity": "adult_obesity",
    }

    results = process.extract(txt, var_list.keys())
    var_names = [var_list[keyword] for keyword, score in results if score >= 90]
    return var_names
