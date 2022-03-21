# http://www.quanben.io

import requests
import random
import re
from lxml import etree
from lxml.etree import ElementBase

from .base import *


class QuanBenNovelParser(BaseNovelParser):
    _HOST_WWW = "www.quanben.io"
    _SERVER = f"http://{_HOST_WWW}"
    _RE_BOOK_ID = re.compile(r"load_more\('(\S*?)'\)")
    _RE_STATIC_CHARS = re.compile(r"var staticchars=\"(\S*?)\";")
    _RE_CALLBACK = re.compile(r"var callback='(\S*?)';")
    _RE_MORE_DETAIL_CONTENT = re.compile(r"\"content\":\"(.*?)\"}\);")
    _UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74"

    def __init__(self, novel_id: str):
        super().__init__(novel_id)
        self.client = requests.session()

    @property
    def name(self) -> str:
        return "quanben"

    def parse_index(self) -> List[Tuple[str, str]]:
        url = f"{self._SERVER}/n/{self.novel_id}/list.html"
        index_list = []
        with self.client.get(url, headers={
            "Host": self._HOST_WWW,
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "DNT": "1",
            "Referer": f"{self._SERVER}/n/{self.novel_id}/",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self._UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }) as r:
            if r.status_code == 403:
                raise ConnectionError("Main index: 403 Forbidden")
            document: ElementBase = etree.HTML(r.text)
            self.title = document.xpath("//html/body/h1/text()")[0].strip()
            index_elements: List[ElementBase] = document.xpath("//body/div[@class='box']/ul[@class='list3']")
            assert len(index_elements) == 2
            index_list.extend(self._parse_index_list(index_elements[0]))
            index_list.extend(self._load_more_index(document, url))
            index_list.extend(self._parse_index_list(index_elements[1]))
        return index_list

    def _parse_index_list(self, list_element: ElementBase) -> List[Tuple[str, str]]:
        index = list_element.xpath("li/a[@itemprop='url']")
        return [(i.xpath("span/text()")[0].strip(), self._SERVER + i.attrib["href"]) for i in index]

    def _load_more_index(self, document: ElementBase, from_url: str) -> List[Tuple[str, str]]:
        js_on_click = document.xpath("//div[@id='detail']/div[@class='more']/a")[0].attrib["onclick"]
        book_id = self._RE_BOOK_ID.search(js_on_click).groups()[0]
        js_head = document.xpath("/html/head/script[1]/text()")[0]
        static_chars = self._RE_STATIC_CHARS.search(js_head).groups()[0]
        callback = self._RE_CALLBACK.search(js_head).groups()[0]
        encode_callback = self._encode_callback(static_chars, callback)
        resource_url = f"{self._SERVER}/index.php?c=book&a=list.jsonp&callback={callback}&book_id={book_id}&b={encode_callback}"
        with self.client.get(resource_url, headers={
            "Host": self._HOST_WWW,
            "Connection": "keep-alive",
            "DNT": "1",
            "Referer": from_url,
            "User-Agent": self._UA,
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }) as r:
            if r.status_code == 403:
                raise ConnectionError("More index: 403 Forbidden")
            response_content = r.content.decode("unicode-escape").replace(r"\/", "/").replace("\r", "")
            more_html = self._RE_MORE_DETAIL_CONTENT.search(response_content).groups()[0]
            more_document: ElementBase = etree.HTML(more_html)
            list_element = more_document.xpath("//ul[@class='list3']")[0]
        return self._parse_index_list(list_element)

    @staticmethod
    def _encode_callback(static_chars: str, text: str) -> str:
        result = []
        for c in text:
            num_0 = static_chars.index(c)
            if num_0 == -1:
                code = c
            else:
                code = static_chars[(num_0 + 3) % 62]
            num_1 = int(random.random() * 62)
            num_2 = int(random.random() * 62)
            result.append(static_chars[num_1] + code + static_chars[num_2])
        return "".join(result)

    def parse_content(self, index_url: str, title: Optional[str] = None) -> Optional[str]:
        with self.client.get(index_url, headers={
            "Host": self._HOST_WWW,
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "DNT": "1",
            "Referer": f"{self._SERVER}/n/{self.novel_id}/list.html",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self._UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }) as r:
            if r.status_code == 403:
                raise ConnectionError("Chapater content: 403 Forbidden")
            document: ElementBase = etree.HTML(r.text)
            content: ElementBase = document.xpath("//div[@id='content']")[0]
            text_list = [i.strip() for i in content.itertext() if not i.isspace() and len(i) > 0]
            return '\r\n'.join(text_list)
