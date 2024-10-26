# https://www.hzpxw.net
import re

import requests
from lxml import etree
from lxml.etree import ElementBase

from .base import *


class HzpxwNovelParser(BaseNovelParser):
    _SERVER = "https://www.hzpxw.net"

    def __init__(self, novel_id: str):
        super().__init__(novel_id)
        self._client = requests.Session()

    @property
    def name(self) -> str:
        return "hzpxw"

    def parse_index(self) -> List[Tuple[str, str]]:
        url = f"{self._SERVER}/xinwen/{self.novel_id}/9999999999/"
        index_result = []
        with self._client.get(url) as r:
            document: ElementBase = etree.HTML(r.text)
            self.title: str = document.xpath("//*[@id='info']/h1/text()")[0].strip()
            pages_url = [f"{self._SERVER}{i}" for i in document.xpath("//*[@id='list']/dl/div[1]/select/option/@value") if ".html" not in i and len(i) > 0]
            index_result.extend(self._parse_index(document))
        for page_url in pages_url:
            with self._client.get(page_url) as r:
                document: ElementBase = etree.HTML(r.text)
                index_result.extend(self._parse_index(document))
        return index_result

    @staticmethod
    def _parse_index(document: ElementBase) -> List[Tuple[str, str]]:
        index_list: ElementBase = document.xpath("//*[@id='list']/dl")[0]
        index_temp = []
        for index_node in index_list.iterchildren():
            index_node: ElementBase
            if index_node.tag == "dt":
                index_divider = index_node.xpath("./text()")
                index_divider.extend(index_node.xpath("./*/text()"))
                if any("正文目录" in i or "最新章节" in i for i in index_divider):
                    index_temp.clear()
            elif index_node.tag == "dd":
                index_name = "".join(index_node.xpath("./a/text()"))
                index_href = "".join(index_node.xpath("./a/@href"))
                if len(index_name) > 0 and len(index_href) > 0 and "返回" not in index_name and "第一页" not in index_name:
                    index_temp.append((index_name, index_href))
        return index_temp

    def parse_content(self, index_url: str, title: Optional[str] = None) -> Optional[str]:
        text = []
        while True:
            url = f"{self._SERVER}{index_url}"
            with self._client.get(url) as r:
                document: ElementBase = etree.HTML(r.text)
                content: ElementBase = document.xpath("//*[@id='content']")[0]
                text.extend([i.strip() for i in content.itertext() if not i.isspace() and len(i) > 0])
                next_page: str = document.xpath("//div[@class='bottem1']/a[contains(text(), '下一页')]/@href")[0]
                if re.search(r"_\d+\.html", next_page):
                    index_url = next_page
                else:
                    break
        return '\r\n'.join(text)
