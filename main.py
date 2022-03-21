from novel_sources import *

novel_id = "剑来"
parser_type = AixdzcNovelParser


def test():
    parser = parser_type(novel_id)
    index = parser.parse_index()
    print(f"Book: {parser.title}")
    print(f"Total: {len(index)}")
    print(f"Index: {index[0][0]} ... {index[len(index) - 1][0]}")
    if len(index) > 0:
        print(parser.parse_content(index[0][1]))


def main():
    download = Downloader(parser_type, download_dir="Downloads", overwrite=False)
    download.start(novel_id)


if __name__ == '__main__':
    main()
    # test()
