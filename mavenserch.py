import random
import sys
import time
from ichrome import AsyncChromeDaemon
import asyncio
from lxml import etree
from urllib.parse import urljoin
import json
from py2neo import Graph, Node, Relationship
from py2neo.matching import *

graph = Graph("bolt://192.168.112.232:7687", auth=("neo4j", "      "))
node_matcher = NodeMatcher(graph)

url = "https://mvnrepository.com"
result = {}
page = 8
def save_value(value, href):
    return {"value": string_handle(value), "href": str(href)}



def string_handle(string):
    if isinstance(string, str):
        return string.replace("/r", "").replace("/n", "").replace("\\n", "").replace("\\r", "").strip()
    else:
        return string
def iter_element(elements):
    result = []
    for element in elements:
        href = element.xpath("./@href")
        if not href:
            href = element.xpath("./@src")
        if href:
            href = href[0]
        name = string_handle(element.xpath("./text()"))
        if not name and not href:
            continue
        else:
            if isinstance(name, list) and len(name)  == 1:
                name = name[0]
            if href and href.startswith("/"):
                href = urljoin(url, href)
            result.append(save_value(name, href))
    if len(result) == 1:
        result = result[0]
    if not result:
        result = elements.text
    return result

def iter_element_text(element):
    if element.text:
        string = element.text
    elif element.xpath("./text()"):
        string = string_handle(element.xpath("./text()")[0])
    else:
        string = ""
    for sub_element in element:
        a = iter_element_text(sub_element)
        if a:
            string = " ".join([string, a])
    return string.strip()


async def run():
    number = 0
    async with AsyncChromeDaemon(debug=False) as cd:
        async with cd.connect_tab() as tab:
            result = []
            nodes = list(node_matcher.match("Library"))
            random.shuffle(nodes)
            for i, node in enumerate(nodes):
                library = node["library"]
                group = node["vendor"]
                if "Tags" not in node:
                    html = ""
                    while True:
                        url = f"https://mvnrepository.com/artifact/{group}/{library}"
                        await tab.set_url(url)
                        html = await tab.html
                        time.sleep(1)
                        if html and "error-information-popup" not in html and"403 Forbidden"not in html and "Checking if the site" not in html and "Not Found" not in html:
                            try:
                                data = single_library_parse(html)
                            except:
                                print(url)
                                continue
                            node.update(data)
                            graph.push(node)
                            break
                        elif "Checking if the site" in html or "403 Forbidden" in html:
                            time.sleep(20)
                            print("403")
                            continue
                        elif "Not Found" in html:
                            graph.delete(node)
                            print("404")
                            break
                        else:
                            print("reload")
                            continue

                else:
                    print("pass")
                print(f"{i}/{len(nodes)}")




def single_library_parse(html_finally):
    library = {}
    tables_1 = etree.HTML(html_finally).xpath(
        '''//div[contains(@class,"content")]/table[contains(@class,"grid")][1]''')

    description = etree.HTML(html_finally).xpath(
        '''//div[contains(@class,"im-description")]''')[0]
    description = iter_element_text(description)

    name = etree.HTML(html_finally).xpath(
        '''///h2[contains(@class,"im-title")]''')[0]
    name = iter_element_text(name)


    org = etree.HTML(html_finally).xpath(
        '''//div[contains(@class,"breadcrumb")]/a''')[1]
    org = iter_element_text(org)
    library["description"] = description
    if tables_1:
        tables_1 = tables_1[0]
        for table in tables_1:
            tr_lists = table.xpath("./tr")
            if len(tr_lists) > 0:
                for tr in tr_lists:
                    th_text = tr.xpath("./th")[0].text
                    th_text = string_handle(th_text)
                    if th_text=="Tags":
                        repos = tr.xpath("./td/a")
                        td_text = []
                        for repo in repos:
                            td_text.append(str(repo.xpath("./text()")[0]))
                    else:
                        td_text = tr.xpath("./td")[0]
                        td_text = iter_element_text(td_text)

                    td_text = string_handle(td_text)
                    if th_text == "Used By":
                        td_text = td_text.split("\n")[0]
                    library[th_text] = td_text


    return library

if __name__ == '__main__':
    asyncio.run(run())



