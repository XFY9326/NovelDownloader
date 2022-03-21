from novel_sources import *

novel_id = "aoshidanshen"
parser_type = QuanBenNovelParser


def test():
    parser = parser_type(novel_id)
    index = parser.parse_index()
    print(f"Book: {parser.title}")
    print(f"Total: {len(index)}")
    print(f"Index: {index[0][0]} ... {index[len(index) - 1][0]}")
    if len(index) > 0:
        print(parser.parse_content(index[0][1]))


def main():
    download = Downloader(parser_type, "Downloads")
    download.start(novel_id)


if __name__ == '__main__':
    # main()
    test()
