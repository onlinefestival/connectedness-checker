from bs4 import BeautifulSoup
import requests
import sys
from hashlib import md5
from urllib.parse import urljoin
import os


def check_statement(url, original_hash):
    # print("get", url)
    statement_text = requests.get(url).text

    # print("statement", statement_text)

    statement_hash = md5(statement_text.encode('utf-8')).hexdigest()

    # print("statement md5:", statement_hash)

    if statement_hash != original_hash:
        # print("wrong statement")
        return False
    else:
        return True

def get_statement_hash(filename):
    # get original curational statement
    original_statement = open(filename).read()
    original_hash = md5(original_statement.encode('utf-8')).hexdigest()

    return original_hash

# returns (verified, links)
def get_page_info(url, original_hash):
    print("get", url)
    page_text = requests.get(url).text

    soup = BeautifulSoup(page_text, 'lxml')

    verified = False
    links = []
    statements_url = []

    for child in soup.recursiveChildGenerator():
        if child.name == "a" and 'rel' in child.attrs:
            # print(child)
            if child.attrs["rel"][0] == "onlinefestival":
                links.append(urljoin(url, child.attrs["href"]))
            elif child.attrs["rel"][0] == "onlinefestivalstatement":
                statements_url.append(urljoin(url, child.attrs["href"]))

    if(len(statements_url) != 1):
        print("wrong statements count", len(statements_url))
        verified = False
    else:
        if check_statement(statements_url[0], original_hash):
            print("statement verified")
            verified = True
        else:
            print("wrong statement")
            verified = False

    print("links:", links)

    return verified, links
                    
def handle_link(url_item, link_map, original_hash):
    url = url_item["url"]

    verified, links = get_page_info(url, original_hash)

    if not verified or links == []:
        print(url, "unverified", verified, len(links))
        return False, link_map

    for link in links:
        if link not in [x["url"] for x in link_map]:
            print("new url", url)

            link_map_item = {
                "url": link,
                "prev": url_item,
                "verified": False
            }

            link_map.append(link_map_item)

            status, link_map = handle_link(link_map_item, link_map, original_hash)

    return True, link_map

    
url = sys.argv[1]

original_hash = get_statement_hash("forecast2022.txt")

link_map_item = {"url": url, "prev": None, "verified": False}
link_map = [link_map_item]

status, new_link_map = handle_link(link_map_item, link_map, original_hash)

print("link map", new_link_map)