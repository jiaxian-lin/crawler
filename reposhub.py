import sys
import time

from bs4 import BeautifulSoup
from ichrome import AsyncChromeDaemon
import asyncio
from lxml import etree
from urllib.parse import urljoin
import json
url = "https://mvnrepository.com"
result = {}
page = 1
url_list = {}
def save_value(value, href):
    return {"value": string_handle(value), "href": href}

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
    return string


async def run():
    async with AsyncChromeDaemon(debug=False) as cd:
        async with cd.connect_tab() as tab:
            # 获取每个类别的url
            page = 1
            while page<10:
                url = f"https://reposhub.com/javascript/?pg={page}"
                await tab.set_url(url)
                time.sleep(1)
                html = await tab.html
                html_parser = BeautifulSoup(html, features="html.parser")
                libs_div = html_parser.find_all("div", class_='row row-sm')[0]
                librs = libs_div.find_all('div', class_='m-l-sm m-t-xxs m-r-sm text-md font-bold')
                page_div = html_parser.find_all("div", class_="text-center m-b-sm")[0]

                for lib in librs:
                    try:
                        lib_url = lib.find_all('a')[0].get("href")
                        await tab.set_url(lib_url)
                        time.sleep(0.5)
                        html = await tab.html
                        html_parser = BeautifulSoup(html, features="html.parser")
                        informations = html_parser.find_all('table', class_="table table-striped m-b-none")[0].find_all(
                            'td')
                        repo_title_div = html_parser.find_all('h1', class_='h3 text-dark m-b-sm')[0]
                        repo_name = str(repo_title_div.next)
                        cate = informations[0].text.replace("\n", "").split("/")[-1]
                        if cate not in result:
                            result[cate] = {}
                        result[cate][repo_name] = {}
                        lib_dict = result[cate][repo_name]

                        lib_dict["category"] = informations[0].text.replace("\n", "").split(":")[-1]
                        lib_dict["watchers"] = informations[1].text.split(":")[-1]
                        lib_dict["stars"] = informations[2].text.split(":")[-1]
                        lib_dict["fork"] = informations[3].text.split(":")[-1]
                        lib_dict["last_update"] = informations[4].text.split(":")[-1]
                        github_link = html_parser.find_all('div', class_="m text-ellipsis")[0]
                        github_link = github_link.find_all('a')[0].next_element
                        lib_dict["github_link"] = github_link
                        print(lib_dict["category"], repo_name)
                    except:
                        continue

                page += 1
                if not page_div.find_all('a'):
                    break
                for page_info in page_div.find_all("a"):
                    if page_info.text == str(page):
                        break
                else:
                    break
                continue

if __name__ == '__main__':
    try:
        asyncio.run(run())
    except:
        with open(f"./reposhub_js.json", mode="w", encoding='utf-8') as f:
            json.dump(result, f)
    with open(f"./reposhub_js.json", mode="w", encoding='utf-8') as f:
        json.dump(result,f)
