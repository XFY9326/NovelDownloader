from novel_sources import *

novel_id = "4000"
parser_type = TrxsNovelParser


def test():
    parser = parser_type(novel_id)
    index = parser.parse_index()
    print(f"Book: {parser.title}")
    print(f"Total: {len(index)}")
    print(index)
    if len(index) > 0:
        print(parser.parse_content(index[0][1]))


def main():
    download = Downloader(parser_type, "Downloads")
    download.start(novel_id)


if __name__ == '__main__':
    main()
    # test()
