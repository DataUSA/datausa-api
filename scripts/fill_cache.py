import requests
import json
import time
import threading
import os
from multiprocessing import Pool
from requests.auth import HTTPBasicAuth


def url_to_json(url):
    print url
    result = requests.get(url).json()
    if 'data' in result:
        return result['data'], result['headers']
    raise Exception("No data!")

def crawl_page(moi):
    display_id,attr_kind = moi
    page = 'http://beta.datausa.io/profile/{}/{}/'.format( attr_kind, display_id)
    print page, "getting..."
    r = requests.get(page, auth=HTTPBasicAuth('datausa', os.environ.get('DATAUSA_WEB_PW', '')))
    if r.status_code != 200:
        print "PAGE ERROR", page, r.status_code

def crawl_attr(base_url, attr_kind='country'):
    data, headers = url_to_json('{}/attrs/search?q=&kind={}&limit=100000'.format(base_url, attr_kind))
    data = sorted(data, key=lambda obj: obj[headers.index('zvalue')], reverse=True)
    mydata = [[country[headers.index('id')], attr_kind] for country in data]
    pool = Pool(5)
    pool.map(crawl_page, mydata)



def main(base_url="http://db.datausa.io", attr="geo"):
    if not base_url.startswith('http://'):
        base_url = 'http://' + base_url
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    attrs = attr.split(",")
    print "Waiting for crawl to complete..."
    for attr in attrs:
        crawl_attr(base_url, attr)
    print "Crawl complete!"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        main()
    else:
        attr = sys.argv[2] if len(sys.argv) >= 3 else "geo"
        main(sys.argv[1], attr)
