import requests
import json
import time
import threading
import os
from requests.auth import HTTPBasicAuth
import click

def url_to_json(url):
    print url
    result = requests.get(url).json()
    if 'data' in result:
        return result['data'], result['headers']
    raise Exception("No data!")

def crawl_page(site_url, moi):
    display_id,attr_kind = moi
    if not display_id:
        print "skipping", display_id, attr_kind
    page = u'{}/profile/{}/{}/'.format(site_url, attr_kind, display_id)
    print page, "getting..."
    r = requests.get(page, auth=HTTPBasicAuth('sunbird', os.environ.get('DATAUSA_WEB_PW', '')))
    if r.status_code != 200:
        if r.status_code == 401:
            raise Exception("You may have forgotten to set DATAUSA_WEB_PW env var (or provided a bad PW).\nWe need this because the site is password protected")
        print "PAGE ERROR", page, r.status_code

def crawl_attr(api_url, site_url, attr_kind, offset, sumlevel):
    sumlevel = "" if not sumlevel else "sumlevel={}".format(sumlevel)
    data, headers = url_to_json('{}/attrs/search?q=&kind={}&limit=110000&offset={}&{}'.format(api_url, attr_kind, offset, sumlevel))
    data = sorted(data, key=lambda obj: obj[headers.index('zvalue')], reverse=True)
    if attr_kind != 'geo':
        mydata = [[country[headers.index('id')], attr_kind] for country in data]
    else:
        mydata = [[country[headers.index('url_name')], attr_kind] for country in data]

    for x in mydata:
        crawl_page(site_url, x)

def fix_url(my_url):
    if not my_url.startswith('http://'):
        my_url = 'http://' + my_url
    if my_url.endswith('/'):
        my_url = my_url[:-1]
    return my_url

@click.command()
@click.option('--api_url', default="http://db.datausa.io", help='API Url')
@click.option('--site_url', default="http://beta.datausa.io", help='Site Url')
@click.option('--attr', default="geo", help="attr kind")
@click.option('--offset', default=0, help="offset in list")
@click.option('--sumlevel', default=None, help="attr sumlevel")
def main(api_url, site_url, attr, offset, sumlevel):
    api_url = fix_url(api_url)
    site_url = fix_url(site_url)
    attrs = attr.split(",")
    print "Waiting for crawl to complete..."
    for attr in attrs:
        crawl_attr(api_url, site_url, attr, offset, sumlevel)
    print "Crawl complete!"

if __name__ == "__main__":
    main()
