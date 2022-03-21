# https://www.xiashuyun.com
import requests
from lxml import etree
from lxml.etree import ElementBase

from .base import *


class XiaShuYunNovelParser(BaseNovelParser):
    _HOST_WWW = "www.xiashuyun.com"
    _HOST_MOBILE = "m.xiashuyun.com"
    _SERVER = f"https://{_HOST_WWW}"

    @property
    def name(self) -> str:
        return "xiashuyun"

    def parse_index(self) -> List[Tuple[str, str]]:
        url = f"{self._SERVER}/{self.novel_id}/chapters.html"
        index_list = []
        with requests.get(url) as r:
            document: ElementBase = etree.HTML(r.text)
            self.title = document.xpath("//*[@id='info']/div[1]/h1/text()")[0].replace("txt下载", "").strip()
            index: List[ElementBase] = document.xpath("//ul[@class='list']/li/a")
            index_list.extend([(i.text.strip(), self._SERVER + i.attrib["href"]) for i in index])
        return index_list

    def parse_content(self, index_url: str, title: Optional[str] = None) -> Optional[str]:
        content = ""
        page_url = index_url.replace(self._HOST_WWW, self._HOST_MOBILE)
        has_next_page = True
        while has_next_page:
            with requests.get(page_url) as r:
                document: ElementBase = etree.HTML(r.text)
                if title is None:
                    title = self.__parse_title(document)
                content += self.__parse_content(document)
                # noinspection SpellCheckingInspection
                next_page: ElementBase = document.xpath("//div[@class='articlebtn']/a[@class='nextinfo']")[0]
                # noinspection SpellCheckingInspection
                if "下一页" in next_page.text and "readend.html" not in next_page.attrib["href"]:
                    page_url = (self._SERVER + next_page.attrib["href"]).replace(self._HOST_WWW, self._HOST_MOBILE)
                    content += "\r\n"
                else:
                    has_next_page = False
        return title + "\r\n\r\n" + content

    @staticmethod
    def __parse_title(document: ElementBase) -> str:
        # noinspection SpellCheckingInspection
        return document.xpath("//div[@class='content']/h1[@class='titlename']/text()")[0]

    @staticmethod
    def __parse_content(document: ElementBase) -> str:
        # noinspection SpellCheckingInspection
        content: ElementBase = document.xpath("//div[@class='content']/div[contains(@class,'articlecon')]")[0]
        return '\r\n'.join([i.strip() for i in content.itertext() if not i.isspace() and "点击下一页" not in i and len(i) > 0])
