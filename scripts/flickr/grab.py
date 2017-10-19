import csv, flickr, os, short, sys, urllib
from config import FLICKR_DIR
from datausa.database import db
from datausa.attrs.views import attr_map
from PIL import Image as pillow
# from scripts.flickr.analyze import LICENSES, MAX_SIDE

MAX_SIDE = 1600
LICENSES = ["4", "5", "7", "8", "9", "10"]

def read_csv():

    thumb_side = 425
    quality = 90

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
    smallImages = []
    goodImages = []
    removedImages = []

    # skip = True

    if not os.path.exists(imgdir):
        os.makedirs(imgdir)

    if not os.path.exists(thumbdir):
        os.makedirs(thumbdir)

    for row in input_file:
        update = False
        uid = row["id"]

        # if uid == "31000US12700":
        #     skip = False
        #
        # if skip:
        #     continue

        image_only = attr_type == "geo"

        if not image_only or (image_only and "image_link" in row and row["image_link"] != ""):

            if "level" in row:
                attr = table.query.filter_by(id=uid,level=row["level"]).first()
            else:
                attr = table.query.get(uid)

            if attr and "image_link" in row:
                image = row["image_link"]
                # if image: # Use this if statement instead of the next line to force an update on all images.
                if image and attr.image_link != image:

                    if "photolist" in image:
                        image = image.split("/in/photolist")[0]

                    pid = image.split("/")[-1]
                    if "flic.kr" not in image:
                        image = "http://flic.kr/p/{}".format(short.encode(pid))

                    photo = flickr.Photo(pid)
                    try:
                        photo._load_properties()
                    except:
                        removedImages.append(uid)
                        continue

                    image = {"id": uid, "url": image, "license": photo._Photo__license}

                    if image["license"] not in LICENSES:
                        badImages.append(image)
                    else:
                        sizes = [p for p in photo.getSizes() if p["width"] >= MAX_SIDE]
                        if len(sizes) == 0:
                            smallImages.append(image)
                        else:
                            download_url = min(sizes, key=lambda item: item["width"])["source"]

                            imgpath = os.path.join(imgdir, "{}.jpg".format(uid))
                            thumbpath = os.path.join(thumbdir, "{}.jpg".format(uid))

                            urllib.urlretrieve(download_url, imgpath)

                            img = pillow.open(imgpath).convert("RGB")

                            img.thumbnail((MAX_SIDE, MAX_SIDE), pillow.ANTIALIAS)
                            img.save(imgpath, "JPEG", quality=quality)

                            img.thumbnail((thumb_side, thumb_side), pillow.ANTIALIAS)
                            img.save(thumbpath, "JPEG", quality=quality)

                            author = photo._Photo__owner
                            author = author.realname if author.realname else author.username
                            image["author"] = author.replace("'", "\\'")
                            goodImages.append(image)

                            attr.image_link = image["url"]
                            attr.image_author = image["author"]
                            update = True

                # set False to True to force thumbnails
                elif False and image:

                    imgpath = os.path.join(imgdir, "{}.jpg".format(uid))
                    thumbpath = os.path.join(thumbdir, "{}.jpg".format(uid))

                    img = pillow.open(imgpath).convert("RGB")

                    img.thumbnail((thumb_side, thumb_side), pillow.ANTIALIAS)
                    img.save(thumbpath, "JPEG", quality=quality)

            if not image_only:
                name = row["name"]
                if attr and name and attr.name != name:
                    attr.name = name
                    update = True

            if "image_meta" in row:
                meta = row["image_meta"]
                if attr and meta and attr.image_meta != meta:
                    attr.image_meta = meta
                    update = True

            if update:
                db.session.add(attr)
                db.session.commit()

            # break

    print "{} new images have been processed.".format(len(goodImages))
    if len(badImages) > 0:
        print "The following images have bad licenses: {}".format(", ".join([i["id"] for i in badImages]))
    if len(smallImages) > 0:
        print "The following images are too small: {}".format(", ".join([i["id"] for i in smallImages]))
    if len(removedImages) > 0:
        print "The following images have been removed: {}".format(", ".join([i for i in removedImages]))



if __name__ == '__main__':
    read_csv()
