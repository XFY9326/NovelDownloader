# http://www.buxia.net
import requests
import re
from lxml import etree
from lxml.etree import ElementBase

from .base import *


class WuShuangNovelParser(BaseNovelParser):
    _SERVER = "http://www.buxia.net"

    @property
    def name(self) -> str:
        return "wushuang"

    def parse_index(self) -> List[Tuple[str, str]]:
        url = f"{self._SERVER}/xiaoshuo/{self.novel_id}/"
        index_list = []
        with requests.get(url) as r:
            document: ElementBase = etree.HTML(r.text)
            self.title = document.xpath("//div[@class='bookinfo']/h1[@class='booktitle']/text()")[0].strip()
            index: List[ElementBase] = document.xpath("//*[@id='showmore01']/dd/a")
            index_list.extend([(i.text.strip(), self._SERVER + i.attrib["href"]) for i in index])
        return index_list

    def parse_content(self, index_url: str, title: Optional[str] = None) -> Optional[str]:
        content = ""
        page_url = index_url
        has_next_page = True
        while has_next_page:
            with requests.get(page_url) as r:
                document: ElementBase = etree.HTML(r.text)
                if title is None:
                    title = self.__parse_title(document)
                content += self.__parse_content(document)
                next_page: ElementBase = document.xpath("//*[@id='pb_next']")[0]
                if "下一页" in next_page.text:
                    page_url = self._SERVER + next_page.attrib["href"]
                else:
                    has_next_page = False
        return title + "\r\n\r\n" + content

    @staticmethod
    def __parse_title(document: ElementBase) -> str:
        return document.xpath("//*[@id='nr_title']/text()")[0]

    @staticmethod
    def __parse_content(document: ElementBase) -> str:
        elements: List[ElementBase] = document.xpath("//div[@id='txt']/p[@data-id != '0' and @data-id != '99']")
        elements = sorted(elements, key=lambda x: int(x.attrib["data-id"]))
        content = []
        for i, element in enumerate(elements):
            text = "\r\n".join([i.replace("\xa0", "") for i in element.itertext() if not i.isspace() and len(i) > 0])
            if i == len(elements) - 1 and "本章未完" in text:
                text = re.sub(r"（本章未完.*?）", "", text)
            content.append(text.strip())
        return '\r\n'.join(content)
