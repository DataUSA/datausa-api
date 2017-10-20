import csv, flickr, short, sys

MAX_SIDE = 1400
LICENSES = ["4", "5", "7", "8", "9", "10"]

def read_csv():

    if len(sys.argv) < 3:
        print "------------------------------------------"
        print "ERROR: Script requires 2 variables, an attribute type and a filename."
        print "Example: python grab.py cip file.csv"
        print "------------------------------------------"
        return

    attr_type = sys.argv[1]
    csvReader = csv.DictReader(open(sys.argv[2]))
    input_file = list(csvReader)
    images = []

    print "Analyzing {} images".format(attr_type.upper())
    for index, row in enumerate(input_file):
        sys.stdout.write("\r{} of {}".format(index, len(input_file)))
        sys.stdout.flush()
        uid = row["id"]

        if "image_link" in row and row["image_link"] != "":

            image = row["image_link"]
            if "photolist" in image:
                image = image.split("/in/photolist")[0]

            pid = image.split("/")[-1]
            if "flic.kr" not in image:
                image = "http://flic.kr/p/{}".format(short.encode(pid))


            image = {"id": uid, "url": image, "small": False, "removed": False}
            row["error"] = ""

            photo = flickr.Photo(pid)
            try:
                photo._load_properties()
            except:
                image["removed"] = True
                row["error"] = "removed"

            if photo._Photo__license:
                image["license"] = photo._Photo__license
                if image["license"] in LICENSES:
                    if len([p for p in photo.getSizes() if p["width"] >= MAX_SIDE]) == 0:
                        image["small"] = True
                        row["error"] = "resolution"
                else:
                    row["error"] = "license-{}".format(image["license"])

            images.append(image)

    print "\n"
    print "Outputing to CSV..."
    with open(sys.argv[2].replace(".csv", "-update.csv"), 'wb') as f:
        w = csv.DictWriter(f, None)

        w.fieldnames = csvReader.fieldnames
        w.writerow(dict((h, h) for h in csvReader.fieldnames))

        for row in input_file:
            w.writerow(row)

    print "\n"
    num_images = float(len(images))
    print "{} images have been analyzed".format(int(num_images))
    bads = sum(1 for image in images if "license" in image and image["license"] not in LICENSES)
    print "{} ({}%) have bad licenses".format(bads, round((bads / num_images) * 100))
    smalls = sum(1 for image in images if image["small"])
    print "{} ({}%) are too small".format(smalls, round((smalls / num_images) * 100))
    missing = sum(1 for image in images if image["removed"])
    print "{} ({}%) have been removed from Flickr".format(missing, round((missing / num_images) * 100))

if __name__ == '__main__':
    read_csv()
