from datausa import app
from flask import Blueprint, request, jsonify

mod = Blueprint('attrs', __name__, url_prefix='/attrs')
from datausa.attrs.models import Course, Naics, University, Soc, Degree

def show_attrs(attr_obj):
    attrs = attr_obj.query.all()
    data = [a.serialize() for a in attrs]
    return jsonify(data=data)

@mod.route("/<kind>/")
def attrs(kind):
    attr_map = {"soc": Soc, "naics" : Naics, "course": Course,
                "university": University, "degree": Degree}
    if kind in attr_map:
        attr_obj = attr_map[kind]
        return show_attrs(attr_obj)
    raise Exception("Invalid attribute type.")

app.register_blueprint(mod)