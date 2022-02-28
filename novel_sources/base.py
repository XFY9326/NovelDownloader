from abc import abstractmethod, ABCMeta
from typing import List, Tuple, Optional


class BaseNovelParser(metaclass=ABCMeta):
    def __init__(self, novel_id: str):
        self.novel_id = novel_id
        self.title = novel_id

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    def ep_divider(self) -> bool:
        return True

    @abstractmethod
    def parse_index(self) -> List[Tuple[str, str]]:
        raise NotImplementedError

    @abstractmethod
    def parse_content(self, index_url: str, title: Optional[str] = None) -> str:
        raise NotImplementedError
