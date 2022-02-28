# http://www.lanlanguoji.com
import requests
from lxml import etree
from lxml.etree import ElementBase

from .base import *


class LanlanNovelParser(BaseNovelParser):
    _SERVER = "http://www.lanlanguoji.com"

    @property
    def name(self) -> str:
        return "lanlanguoji"

    def parse_index(self) -> List[Tuple[str, str]]:
        url = f"{self._SERVER}/xiaoshuo/{self.novel_id}/"
        index_pages = []
        index_list = []
        with requests.get(url) as r:
            document: ElementBase = etree.HTML(r.text)
            self.title = document.xpath("//*[@class='info']/div[1]/h1/text()")[0]
            index: List[ElementBase] = document.xpath("//*[@id='indexselect']/option")
            index_pages.extend([self._SERVER + i.attrib["value"] for i in index])
            index_list.extend(self.__parse_index(document))
        for page in index_pages[1:]:
            with requests.get(page) as r:
                document: ElementBase = etree.HTML(r.text)
                index_list.extend(self.__parse_index(document))
        return index_list

    def __parse_index(self, document: ElementBase) -> List[Tuple[str, str]]:
        index: List[ElementBase] = document.xpath("//*[@class='container']/div[2]/div[1]/div[2]/ul/li/a")
        return [(i.text, self._SERVER + i.attrib["href"]) for i in index]

    def parse_content(self, index_url: str, title: Optional[str] = None) -> str:
        content = ""
        page_url = index_url
        has_next_page = True
        while has_next_page:
            with requests.get(page_url) as r:
                document: ElementBase = etree.HTML(r.text)
                if title is None:
                    title = self.__parse_title(document)
                content += self.__parse_content(document)
                next_page: ElementBase = document.xpath("//*[@id='next_url']")[0]
                if "下一页" in next_page.text:
                    page_url = self._SERVER + next_page.attrib["href"]
                else:
                    has_next_page = False
        return title + "\r\n\r\n" + content

    @staticmethod
    def __parse_title(document: ElementBase) -> str:
        title: ElementBase = document.xpath("//*[@id='content']/../h1")[0]
        title_str: str = title.text
        if "章" in title_str and "章 " not in title_str:
            title_str = title_str.replace("章", "章 ", 1)
        return title_str

    @staticmethod
    def __parse_content(document: ElementBase) -> str:
        content: ElementBase = document.xpath("//*[@id='content']")[0]
        return '\r\n'.join([i.strip() for i in content.itertext() if not i.isspace() and len(i) > 0])
