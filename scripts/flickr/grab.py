import csv, flickr, os, short, sys, urllib
from config import FLICKR_DIR
from datausa.database import db
from datausa.attrs.views import attr_map
from PIL import Image as pillow

def read_csv():

    if len(sys.argv) < 3:
        print "------------------------------------------"
        print "ERROR: Script requires 2 variables, an attribute type and a filename."
        print "Example: python grab.py cip file.csv"
        print "------------------------------------------"
        return

    attr_type = sys.argv[1]
    if attr_type not in attr_map:
        print "------------------------------------------"
        print "ERROR: Invalid attribute type."
        print "Allowed keys: {}".format(", ".join(attr_map.keys()))
        print "------------------------------------------"
        return
    else:
        table = attr_map[attr_type]

    input_file = csv.DictReader(open(sys.argv[2]))
    imgdir = os.path.join(FLICKR_DIR, attr_type)
    thumbdir = imgdir.replace("splash", "thumb")
    badImages = []
    goodImages = []

    for row in input_file:
        update = False
        uid = row["id"]

        image_only = attr_type == "geo"

        if not image_only or (image_only and "image_link" in row and row["image_link"] != ""):

            if "level" in row:
                attr = table.query.filter_by(id=uid,level=row["level"]).first()
            else:
                attr = table.query.get(uid)

            if attr and "image_link" in row:
                image = row["image_link"]
                if image and attr.image_link != image:

                    if "photolist" in image:
                        image = image.split("/in/photolist")[0]

                    pid = image.split("/")[-1]
                    if "flic.kr" not in image:
                        image = "http://flic.kr/p/{}".format(short.encode(pid))

                    photo = flickr.Photo(pid)
                    photo._load_properties()

                    image = {"id": uid, "url": image, "license": photo._Photo__license}

                    if image["license"] in ["0"]:
                        badImages.append(image)
                    else:

                        author = photo._Photo__owner
                        author = author.realname if author.realname else author.username
                        image["author"] = author.replace("'", "\\'")
                        download_url = max(photo.getSizes(), key=lambda item: item["width"])["source"]

                        if not os.path.exists(imgdir):
                            os.makedirs(imgdir)

                        if not os.path.exists(thumbdir):
                            os.makedirs(thumbdir)

                        imgpath = os.path.join(imgdir, "{}.jpg".format(uid))
                        thumbpath = os.path.join(thumbdir, "{}.jpg".format(uid))

                        urllib.urlretrieve(download_url, imgpath)

                        img = pillow.open(imgpath).convert("RGB")

                        img.thumbnail((1200,1200), pillow.ANTIALIAS)
                        img.save(imgpath, "JPEG", quality=60)

                        img.thumbnail((150,150), pillow.ANTIALIAS)
                        img.save(thumbpath, "JPEG", quality=60)

                        goodImages.append(image)

                        attr.image_link = image["url"]
                        attr.image_author = image["author"]
                        update = True

            if not image_only:
                name = row["name"]
                if attr and name and attr.name != name:
                    attr.name = name
                    update = True

            if update:
                db.session.add(attr)
                db.session.commit()

    print "{} new images have been processed.".format(len(goodImages))
    if len(badImages) > 0:
        print "The following images have bad licenses: {}".format(", ".join([i["id"] for i in badImages]))



if __name__ == '__main__':
    read_csv()
