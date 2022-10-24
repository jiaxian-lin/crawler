import sys
import time
from ichrome import AsyncChromeDaemon
import asyncio
from lxml import etree
from urllib.parse import urljoin
import json
url = "https://mvnrepository.com"
result = {}
page = 1
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
    global page, result
    number = 0
    new_result = {}
    async with AsyncChromeDaemon(debug=False) as cd:
        async with cd.connect_tab() as tab:
            new_result = {}
            html = ""
            while True:
                await tab.set_url("https://mvnrepository.com/open-source?p={}".format(page))
                time.sleep(1)
                html = await tab.html
                if html and "error-information-popup" not in html and"403 Forbidden"not in html and "Checking if the site" not in html:
                    break
                elif "Checking if the site" in html or "403 Forbidden" in html:
                    time.sleep(20)
                    continue
                raise Exception
                  # 第一层
            # 获取每个类别的url
            for category_url in etree.HTML(html).xpath("//h4/a/@href"):
                category_url = urljoin("https://mvnrepository.com/open-source", category_url)
                category_name = string_handle(category_url.split("/")[-1]) # 获取类别的名称

                if category_name in result:
                    new_result[category_name] = result[category_name]
                result_categrocy = result[category_name]
                category_url = category_url + "?p={}"
                for library_page in range(1, 16):
                    html = ""
                    while True:
                        await tab.set_url(category_url.format(library_page))
                        await asyncio.sleep(1)
                        html = await tab.html
                        if html and "error-information-popup" not in html and"403 Forbidden"not in html and "Checking if the site" not in html:
                            break
                        elif "Checking if the site" in html or "403 Forbidden" in html:
                            time.sleep(20)
                            continue
                        raise Exception
                    if '<div class="im">' not in html:
                        # print(url.format(i))
                        continue  # 最多的有15页
                    a_lst = etree.HTML(html).xpath("//div[contains(@class,'im')]/a[1]")
                    if len(a_lst) == 0:
                        continue
                    for a in a_lst:
                        number += 1
                        href = urljoin(category_url, "".join(a.xpath("./@href")))
                        html = ""
                        while True:
                            await tab.set_url(href)
                            await asyncio.sleep(1)
                            html = await tab.html
                            if html and "error-information-popup" not in html and "403 Forbidden" not in html and "Checking if the site" not in html:
                                break
                            elif "Checking if the site" in html or "403 Forbidden" in html:
                                time.sleep(20)
                                continue
                            time.sleep(5)

                        library = etree.HTML(html).xpath(
                            '''//div[contains(@id,"maincontent")]/div[2]/div[1]/h2/a[1]/text()''')
                        if library:
                            library = string_handle(library[0])
                        if library not in result_categrocy:
                            result_categrocy[library] = {}

                        version_url_list = []
                        version_tables =etree.HTML(html).xpath("//table[contains(@class,'grid versions')]//tbody")
                        description =  etree.HTML(html).xpath(
                                '''//div[contains(@class,"im-description")]''')[0].text
                        org = etree.HTML(html).xpath('''//div[contains(@class,"breadcrumb")]/a''')[1].text
                        for version_table in version_tables:
                            for s, line in enumerate(version_table):
                                if s == 0 and "rowspan" in etree.tostring(line).decode("utf-8"):
                                    version = str(line.xpath("./td[2]/a/text()")[0])
                                    if version in result_categrocy[library]:
                                        result_categrocy[library][version]["description"] = description
                                        result_categrocy[library][version]["org"] = org
                                        continue
                                    version_url_list.append(line.xpath("./td[2]/a/@href")[0])
                                else:
                                    version = str(line.xpath("./td[1]/a/text()")[0])
                                    if version in result_categrocy[library]:
                                        result_categrocy[library][version]["description"] = description
                                        result_categrocy[library][version]["org"] = org
                                        continue
                                    version_url_list.append(line.xpath("./td[1]/a/@href")[0])
            with open(f"./result_{page}1.json", mode="w", encoding='utf-8') as f:
                json.dump(new_result, f)
            page += 1


if __name__ == '__main__':
    while page < 16:
        with open(f"./result_8.json", mode="r", encoding='utf-8') as f:
            result = json.load(f)
        asyncio.run(run())

