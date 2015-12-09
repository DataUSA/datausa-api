import os
from datausa.database import db
from datausa.attrs.models import Geo, PumsSoc, PumsNaics, Cip


def img_path(attr_obj, attr_kind, attr_data_map):
    '''Given an attr_obj and attr_kind, determine the best static image
    file to use'''
    my_id = attr_obj.id
    if not attr_obj.image_link:
        data, headers = attr_obj.parents(attr_obj.id)
        id_idx = headers.index("id")
        parent_ids = [row[id_idx] for row in data]
        parents = [attr_data_map[x] for x in parent_ids]
        for p in reversed(parents):
            if p.image_link:
                my_id = p.id
                break
    return os.path.join(attr_kind, "{}.jpg".format(my_id))


def update_attr_img_paths(attr_kind):
    attr_map = {"geo": Geo, "cip": Cip, "naics": PumsNaics, "soc": PumsSoc}
    AttrCls = attr_map[attr_kind]
    filters = []
    if attr_kind == 'geo':
        filters = [~Geo.id.startswith("140"), ~Geo.id.startswith("860")]
    all_attrs = AttrCls.query.filter(*filters).all()

    attr_data_map = {a.id : a for a in all_attrs}

    counter = 0
    for attr_obj in all_attrs:
        calculated_img = img_path(attr_obj, attr_kind, attr_data_map)
        if calculated_img != attr_obj.image_path:
            # -- update image link
            attr_obj.image_path = calculated_img
            db.session.add(attr_obj)
            counter += 1
        if counter % 1000 == 0:
            db.session.commit()
            counter = 0

    if counter > 0:
        db.session.commit()

if __name__ == '__main__':
    # geo_obj = Geo.query.filter_by(id='16000US4814880').first()
    # print img_path(geo_obj, "geo")
    # soc_obj = PumsSoc.query.filter_by(id='111021').first()
    # print img_path(soc_obj, "soc")
    for attr_kind in ["naics", "soc", "cip", "geo"]:
        update_attr_img_paths(attr_kind)

