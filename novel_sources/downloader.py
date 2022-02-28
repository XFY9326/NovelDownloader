import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Callable, Optional

from .base import BaseNovelParser


class Downloader:
    def __init__(self, parser_obj: Callable[[str], BaseNovelParser], download_dir: str = "", overwrite: bool = False):
        self._download_dir = download_dir
        self._overwrite = overwrite
        self._parser_obj: Callable[[str], BaseNovelParser] = parser_obj

    def start(self, novel_id: str):
        parser = self._parser_obj(novel_id)
        index = self.__load_index(parser)
        path = self.__prepare_folder(parser)
        self.__launch_tasks(parser, index, path)
        os.sync()
        self.__combine_text_file(parser, path)

    @staticmethod
    def __load_index(parser: BaseNovelParser) -> List[Tuple[str, str]]:
        index = parser.parse_index()
        print(f"Book: {parser.title}")
        print(f"Total: {len(index)}")
        return index

    def __prepare_folder(self, parser: BaseNovelParser) -> str:
        path = os.path.join(self._download_dir, parser.name, parser.novel_id)
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def __launch_tasks(self, parser: BaseNovelParser, index: List[Tuple[str, str]], path: str):
        amount = len(index)
        num_length = len(str(amount))
        with ThreadPoolExecutor() as executor:
            novel_tasks = [executor.submit(self.__download, parser, path, i, num_length, data[1], self._overwrite) for i, data in enumerate(index)]
            retry_tasks = []

            for i, future in enumerate(novel_tasks):
                print(f"\rProgress: {i + 1}/{amount}", end='')
                failed_result = future.result()
                if failed_result is not None:
                    failed_index = failed_result[0]
                    retry_tasks.append(
                        executor.submit(self.__download, parser, path, failed_index, num_length, index[failed_index][1], self._overwrite)
                    )

            if len(retry_tasks) == 0:
                print("\nAll tasks success!")
            else:
                amount = len(retry_tasks)
                error_tasks = []
                for i, future in enumerate(retry_tasks):
                    print(f"\rProgress: {i + 1}/{amount}", end='')
                    error_result = future.result()
                    if error_result is not None:
                        error_tasks.append(error_result)

                if len(error_tasks) == 0:
                    print("\nAll retry tasks success!")
                else:
                    print(f"\n {len(error_tasks)} tasks error!")
                    print(f"Error index:")
                    for task in error_tasks:
                        print(f"\tIndex: {task[0]}  Error: {task[1]}")

        print("Download finish!")

    def __combine_text_file(self, parser: BaseNovelParser, path: str):
        all_text_file = sorted([os.path.join(path, p) for p in os.listdir(path) if not p.startswith(".") and p.endswith(".txt")])
        result_file_name = f"{parser.title}.txt"
        with open(os.path.join(self._download_dir, parser.name, result_file_name), "w") as f:
            for txt_path in all_text_file:
                with open(txt_path, "r") as txt:
                    f.write(txt.read())
                    if parser.ep_divider:
                        f.write("\r\n\r\n\r\n")

        print("Combine finish!")

    @staticmethod
    def __download(parser: BaseNovelParser, path: str, index: int, index_num_length: int, url: str, overwrite: bool) -> \
            Optional[Tuple[int, BaseException]]:
        try:
            text_file_name = (f"%0" + str(index_num_length) + "d.txt") % (index + 1)
            text_file_path = os.path.join(path, text_file_name)
            if overwrite or not os.path.isfile(text_file_path):
                text = parser.parse_content(url)
                if len(text) > 0 and not text.isspace():
                    with open(text_file_path, 'w') as text_file:
                        text_file.write(text)
        except BaseException as e:
            return index, e
