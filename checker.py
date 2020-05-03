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
        print("wrong statement", statement_hash, original_hash)
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

    res = requests.get(url)
    page_text = res.text

    url = res.url

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
            # print("statement verified")
            verified = True
        else:
            print("wrong statement")
            verified = False

    # print("links:", links)

    return url, verified, links
                    
def handle_link(url, link_map, original_hash):
    url, verified, links = get_page_info(url, original_hash)

    # print(link_map)

    if url in link_map:
        # print("url exist, skipping")
        return True, link_map, url

    link_map[url] = []

    if not verified or links == []:
        print(url, "unverified", verified, len(links))
        return False, link_map, url

    for link in links:
        # print("new url", link)
        status, link_map, new_url = handle_link(link, link_map, original_hash)
        link_map[url].append((new_url, status))

    return True, link_map, url

    
url = sys.argv[1]

original_hash = get_statement_hash("forecast2022.txt")

status, new_link_map, _ = handle_link(url, {}, original_hash)

def traversal(node):
    # print("check node", node)
    visited[node] = True

    for next_node in graph[node]:
        if not visited[next_node]:
            traversal(next_node)

graph = {}
for node in new_link_map:
    graph[node] = [x[0] for x in new_link_map[node]]

print()
print("traversal result")
print()

for node in graph:
    visited = {}

    for i in new_link_map:
        visited[i] = False

    # print("root node", graph[node])

    for next_node in graph[node]:
        traversal(next_node)

    a = []
    for i in visited:
        if not visited[i]:
            a.append(i)

    if len(a) > 0:
        print("wrong node", node)

        for i in a:
            print("\t", i)

        print()