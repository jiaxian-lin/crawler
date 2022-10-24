import sys
import time
from ichrome import AsyncChromeDaemon
import asyncio
from lxml import etree
from urllib.parse import urljoin
import json
url = "https://mvnrepository.com"
result = {}
page = 8
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
    async with AsyncChromeDaemon(debug=False) as cd:
        async with cd.connect_tab() as tab:
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

                if category_name not in result:
                    result[category_name] = {}
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
                        for version_table in version_tables:
                            for s, line in enumerate(version_table):
                                if s == 0 and "rowspan" in etree.tostring(line).decode("utf-8"):
                                    version = str(line.xpath("./td[2]/a/text()")[0])
                                    if version in result_categrocy[library]:
                                        continue
                                    version_url_list.append(line.xpath("./td[2]/a/@href")[0])
                                else:
                                    version = str(line.xpath("./td[1]/a/text()")[0])
                                    if version in result_categrocy[library]:
                                        continue
                                    version_url_list.append(line.xpath("./td[1]/a/@href")[0])
                        for tmp_url in version_url_list:
                            if len(result_categrocy[library]) > 100:
                                break
                            version_url = urljoin(href, tmp_url)
                            # print(url)
                            while True:
                                await tab.set_url(version_url)
                                await asyncio.sleep(1)
                                html_finally = await tab.html
                                if html_finally and "error-information-popup" not in html_finally and "403 Forbidden" not in html_finally and "Checking if the site" not in html:
                                    break
                                elif "Checking if the site" in html_finally or "403 Forbidden" in html_finally:
                                    time.sleep(20)
                                    continue
                                raise Exception
                            if "Not Found" in html_finally:
                                continue
                            # 获取库名和版本号
                            version = etree.HTML(html_finally).xpath(
                                '''//div[contains(@id,"maincontent")]/div[2]/div[1]/h2/a[2]/text()''')
                            if version:
                                version = string_handle(version[0])


                            result_library = result_categrocy[library]
                            print(f"{page}, {library_page}, {number},{category_name}, {library}, {version}")
                            # 第一个表格中的内容

                            result_library[version] = single_page_parse(html_finally)
            with open(f"./result_{page}.json", mode="w", encoding='utf-8') as f:
                json.dump(result, f)
            page += 1
            result = {}

def single_page_parse(html_finally):
    tables_1 = etree.HTML(html_finally).xpath(
        '''//div[contains(@id,"maincontent")]/table[contains(@class,"grid")][1]''')
    version = {}


    if tables_1:
        tables_1 = tables_1[0]
        # print(tables_1)
        if len(tables_1) > 0:
            for table in tables_1:
                tr_lists = table.xpath("./tr")
                if len(tr_lists) > 0:
                    for tr in tr_lists:
                        th_text = tr.xpath("./th")[0].text
                        th_text = string_handle(th_text)
                        page_1 = ["Vulnerabilities", "HomePage", "Files", "Organization"]
                        page_2 = ["Categories", "Tags", "Repositories"]
                        if th_text in page_1:
                            td_text = []
                            if th_text == "Vulnerabilities":
                                vulnerabilities = tr.xpath("./td/span/a")
                            else:
                                vulnerabilities = tr.xpath("./td/a")
                            for vulner in vulnerabilities:
                                td_text.append(save_value(vulner.xpath("./text()")[0],vulner.xpath("./@href")[0]))
                        elif th_text in page_2:
                            repos = tr.xpath("./td/a")
                            if len(repos) == 1:
                                if repos[0].xpath("./@href"):
                                    td_text = save_value(repos[0].xpath("./text()")[0], urljoin(url, repos[0].xpath("./@href")[0]))
                                else:
                                    td_text = save_value(repos[0].xpath("./text()")[0], None)
                            else:
                                td_text = []
                                for repo in repos:
                                    if repo.xpath("./@href"):
                                        td_text.append(save_value(repo.xpath("./text()")[0], urljoin(url, repo.xpath("./@href")[0])))
                                    else:
                                        td_text.append(save_value(repo.xpath("./text()")[0], None))
                        elif th_text == "Used By":
                            repos = tr.xpath("./td/a")
                            td_text = save_value(repos[0].xpath(".//b/text()")[0], urljoin(url, repos[0].xpath("./@href")[0]))
                        else:
                            td_text = tr.xpath("./td")[0]
                            td_text = iter_element_text(td_text)

                            td_text = string_handle(td_text)
                            # try:
                            #     dic[leibie][ku][version][th_text]=td_text
                            # except Exception as e:
                            #     continue
                        if th_text not in version:
                            version[th_text] = td_text
                        # print('contents:',contents)

                        # 处理后面表格的内容
    div_s = etree.HTML(html_finally).xpath(
        '''//div[contains(@class,"version-section")]''')
    if div_s:
        div_len = len(div_s)
        for i in range(0, div_len):
            table_name1 = div_s[i].xpath("./h2/text()")
            table_name2 = div_s[i].xpath("./h3/text()")
            table_name = ""
            if table_name1:
                table_name = string_handle(table_name1[0])
            if table_name2:
                table_name = string_handle(table_name2[0])
            table_list = []
            if table_name == "Related Books":
                data_list = div_s[i].xpath(".//table/tbody/tr")
                for data in data_list:
                    table_list.append({"name": data.xpath("./td[2]/a/text()")[0],
                                       "href": data.xpath("./td[2]/a/@href")[0],
                                       "author": data.xpath("./td[2]/span/text()")[0][3:],
                                       "year": string_handle(data.xpath("./td[2]/b/text()")[0])[1:-1]
                                       })
                version[table_name] = table_list
                break

            title_ele = div_s[i].xpath(".//table/thead/tr/th")
            title_list = []
            for title in title_ele:
                title_list.append(string_handle(title.text))
            data_list = div_s[i].xpath(".//table/tbody/tr")
            for singe_data in data_list:
                tmp = {}
                datas = singe_data.xpath("./td")
                for j, data in enumerate(datas):
                    string = iter_element(data)
                    tmp[title_list[j]] = string
                table_list.append(tmp)
            version[table_name] = table_list
    return version


if __name__ == '__main__':
    while page < 9:
        try:
            with open(f"./result_8(2).json", mode="r", encoding='utf-8') as f:
                result = json.load(f)
            asyncio.run(run())
        except:
            with open(f"./result_{page}.json", mode="w", encoding='utf-8') as f:
                json.dump(result, f)
    with open(f"./result_{page}.json", mode="w", encoding='utf-8') as f:
        json.dump(result, f)

