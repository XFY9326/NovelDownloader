# https://www.aixdzs.com

import requests
from lxml import etree
from lxml.etree import ElementBase

from .base import *


class AixdzcNovelParser(BaseNovelParser):
    _HOST_WWW = "www.aixdzs.com"
    _SERVER = f"https://{_HOST_WWW}"

    @property
    def name(self) -> str:
        return "aixdzs"

    def parse_index(self) -> List[Tuple[str, str]]:
        url = f"{self._SERVER}/novel/{self.novel_id}"
        with requests.get(url) as r:
            document: ElementBase = etree.HTML(r.text)
            self.title: str = document.xpath("//div[@class='d_info']/h1/text()")[0].strip()
            index: List[ElementBase] = document.xpath("//div[@id='i-chapter']/ul/li/a")
            return [(i.text.strip(), self._SERVER + i.attrib["href"]) for i in index]

    def parse_content(self, index_url: str, title: Optional[str] = None) -> Optional[str]:
        with requests.get(index_url) as r:
            document: ElementBase = etree.HTML(r.text)
            content: ElementBase = document.xpath("//div[@class='content']")[0]
            title: str = document.xpath("//div[@class='line']/h1/text()")[0]
            text_list = [i.strip() for i in content.itertext() if not i.isspace() and len(i) > 0]
            if len(text_list) == 0:
                return None
            if title not in text_list[0]:
                return title + '\r\n\r\n' + '\r\n'.join(text_list)
            else:
                if len(text_list) > 1:
                    return text_list[0] + '\r\n\r\n' + '\r\n'.join(text_list[1:])
                else:
                    return text_list[0]
