import requests
import json
import time
import threading
from multiprocessing import Pool


def url_to_json(url):
    print url
    result = requests.get(url).json()
    if 'data' in result:
        return result['data'], result['headers']
    raise Exception("No data!")

def crawl_page(moi):
    display_id,attr_kind = moi
    page = 'http://postgres.datawheel.us:81/profile/{}/{}/'.format( attr_kind, display_id)
    print page, "getting..."
    r = requests.get(page)
    print r.status_code

def crawl_attr(base_url, attr_kind='country'):
    data, headers = url_to_json('{}/attrs/search?q=&kind={}&limit=100000'.format(base_url, attr_kind))
    data = sorted(data, key=lambda obj: obj[headers.index('zvalue')], reverse=True)
    mydata = [[country[headers.index('id')], attr_kind] for country in data]
    pool = Pool(5)
    pool.map(crawl_page, mydata)



def main(base_url):
    if not base_url.startswith('http://'):
        base_url = 'http://' + base_url
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    attrs = ['geo']
    thread_list = []
    print "Waiting for crawl to complete..."

    for attr in attrs:
        thread = threading.Thread(target=crawl_attr, args=[base_url, attr])
        thread.start()
        thread_list.append(thread)
    for thread in thread_list:
        thread.join()
    print "Crawl complete!"

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise Exception("Usage: {} BASE_URL".format(__file__))
    main(sys.argv[1])
