import flask

def format(cols, data):
    headers = [col.name for col in cols]
    data = {
            "headers": headers,
            "data": [ list(row) for row in data]
    }
    return flask.jsonify(data)