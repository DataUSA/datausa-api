import flask
import sqlalchemy

from datausa.core import get_columns

def simple_format(cols, data):
    headers = [col if isinstance(col, basestring) else col.key for col in cols]
    data = {
            "headers": list(headers),
            "data": [ list(row) for row in data]
    }
    return flask.jsonify(data)

def query(table, vars_and_vals, shows_and_levels, values=[]):
    filters = [ getattr(table, var) == val for var,val in vars_and_vals.items() ]

    # if values:
    #     pk = [col for col in table.__table__.columns if col.primary_key]
    #     cols = pk + values
    # else:
    cols = get_columns(table)

    data = table.query.with_entities(*cols).filter(*filters).all()    
    return simple_format(cols, data)