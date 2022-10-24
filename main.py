# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import random
from bs4 import BeautifulSoup
import requests, sys
import httpx
my_headers = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
]
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'cookie': 'cf_clearance=jpXJ7Dl9IYP6d.aOTCqv_nrsykNpCDrdRtmItRnCguA-1660456651-0-150; _ga=GA1.2.1580622951.1660456652; __gads=ID=6cd40833113e7ec6-22eeacfb95d50089:T=1660459263:RT=1660459263:S=ALNI_Mbxvs4XGnVTPuX3wnmFlF2WmfGWDQ; _gid=GA1.2.1575661204.1660655796; __gpi=UID=0000089796adabde:T=1660459263:RT=1660826092:S=ALNI_MYPSU68Dey3qBTW01QaPMleadV2Kw; MVN_SESSION=eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7InVpZCI6IjBkYjlhYzkwLTBjYTYtMTFlZC05MjhhLTYzZWY4YzNkOGI1YyJ9LCJleHAiOjE2OTI0MDk1NTQsIm5iZiI6MTY2MDg3MzU1NCwiaWF0IjoxNjYwODczNTU0fQ.VntMmSCa_5iUJ1P9f64Gxg5c3_M3Wl46mHqtZ1VudEk; __cf_bm=nNxhi6yi.U1ABU7oe3gX8tAyP3oXRT45pbOoUAUPGCM-1660873556-0-AZkpabS7I8DTxq+tEXX6kGZlKVI+TtgqcT0ncB/wQpjK1ZRsv8ix2F/KuPBafB/LEqStnHepUmgI4/FqvhHo68lCjUSdxFNMSeCK8d/DsHdIwETL4o8k5Gxochcdp9pZArXfRNDWNK28Xq5zene8eo0jCvrDYwBVIKNAIltL7D5Z',
    'referer': 'https://mvnrepository.com/open-source/testing-frameworks?p=8',
    'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'Windows',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1'
}
pro = ['1.119.129.2:8080', '115.174.66.148', '113.200.214.164']
class downloader(object):

    def __init__(self):
        self.server = 'https://mvnrepository.com/'
        self.target = 'https://mvnrepository.com/'
        self.names = []            #存放章节名
        self.urls = []            #存放章节链接
        self.nums = 0            #章节数

    """
    函数说明:获取下载链接
    Parameters:
        无
    Returns:
        无
    Modify:
        2017-09-13
    """
    def get_download_url(self):
        client = httpx.Client(http2=True)
        result = client.get(url=self.target, headers=headers)
        html = result.text
        div_bf = BeautifulSoup(html, features="html.parser")
        div = div_bf.find_all('div', id="maincontent")
        a_bf = BeautifulSoup(str(div[1]), features="html.parser")
        a = a_bf.find_all('a')
        self.nums = len(a)                                #剔除不必要的章节，并统计章节数
        for each in a:
            self.names.append(each.string)
            self.urls.append(self.server + each.get('href'))

    """
    函数说明:获取章节内容
    Parameters:
        target - 下载连接(string)
    Returns:
        texts - 章节内容(string)
    Modify:
        2017-09-13
    """
    def get_contents(self, target):
        req = requests.get(url=target)
        html = req.text
        bf = BeautifulSoup(html, features="html.parser")
        texts = bf.find_all('div', id = 'content')
        texts = texts[0].text
        texts = '\n\n'.join(str(texts).split())
        return texts

    """
    函数说明:将爬取的文章内容写入文件
    Parameters:
        name - 章节名称(string)
        path - 当前路径下,小说保存名称(string)
        text - 章节内容(string)
    Returns:
        无
    Modify:
        2017-09-13
    """
    def writer(self, name, path, text):
        write_flag = True
        with open(path, 'a', encoding='utf-8') as f:
            f.write(name + '\n')
            f.writelines(text)
            f.write('\n\n')

if __name__ == "__main__":
    dl = downloader()
    dl.get_contents('https://mvnrepository.com/')
    dl.get_download_url()
    print('《剑来》开始下载：')
    for i in range(dl.nums):
        dl.writer(dl.names[i], './剑来.txt', dl.get_contents(dl.urls[i]))
        sys.stdout.write("  已下载:%.3f%%" %float(i*100/dl.nums) + '\r')
        sys.stdout.flush()
    print('《剑来》下载完成')