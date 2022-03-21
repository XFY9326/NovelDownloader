# https://www.trxs.cc/
import requests
from lxml import etree
from lxml.etree import ElementBase

from .base import *


class TrxsNovelParser(BaseNovelParser):
    _SERVER = "https://www.trxs.cc"

    @property
    def name(self) -> str:
        return "trxs"

    @property
    def ep_divider(self) -> bool:
        return False

    def parse_index(self) -> List[Tuple[str, str]]:
        url = f"{self._SERVER}/tongren/{self.novel_id}.html"
        index_list = []
        with requests.get(url) as r:
            r.encoding = "gbk"
            document: ElementBase = etree.HTML(r.text)
            self.title: str = document.xpath("//div[@class='readContent']/div[@class='book_info clearfix']//div[@class='infos']/h1/text()")[0]
            if self.title.endswith("(全本)"):
                self.title = self.title[:self.title.rindex("(全本)")].strip()
            index: List[ElementBase] = document.xpath("//div[@class='readContent']/div[@class='book_list clearfix']/ul/li/a")
            index_list.extend([(i.text.strip(), self._SERVER + i.attrib["href"]) for i in index])
        return index_list

    def parse_content(self, index_url: str, title: Optional[str] = None) -> Optional[str]:
        with requests.get(index_url) as r:
            r.encoding = "gbk"
            document: ElementBase = etree.HTML(r.text)
            content: ElementBase = document.xpath("//div[@class='read_chapterDetail']")[0]
            text_list = [i.strip() for i in content.itertext() if not i.isspace() and len(i) > 0]
            return '\r\n'.join(text_list)
