import argparse
import pathlib

from sigame_tools.datatypes import SIDocument


def query(args):
    path: pathlib.Path = args.PATH
    d: SIDocument = SIDocument.from_siq(path)
    p = d.package
    print(p)


def convert_siq_jsiq(args):
    out_path: pathlib.Path = args.OUTPUT
    path: pathlib.Path = args.PATH
    # if not out_path_root.exists():
    #     raise FileNotFoundError(f"No such directory: '{out_path_root}'")
    if out_path.is_dir():
        out_path = out_path.joinpath(path.stem + ".jsiq.zip")
        # raise NotADirectoryError(f"Not a directory: '{out_path_root}'")
    d: SIDocument = SIDocument.from_siq(path)
    # p = d.package
    d.save_jsiq(out_path)

    # out_path = out_path_root.joinpath(path.stem)
    # if not out_path.exists():
    #     out_path.mkdir()

    # iterable = content_parser.SIJSONEncoder(ensure_ascii=False, indent=2).iterencode(p)
    # with open(out_path.joinpath("content.json"), "w") as fp:
    #     for chunk in iterable:
    #         fp.write(chunk)


def convert_jsiq_siq(args):
    out_path: pathlib.Path = args.OUTPUT
    path: pathlib.Path = args.PATH
    if out_path.is_dir():
        out_path = out_path.joinpath(path.stem.strip(".jsiq") + ".siq")
    d: SIDocument = SIDocument.from_jsiq(path)
    d.save_siq(out_path)


parser = argparse.ArgumentParser(description="SI Game tools CLI")

subparsers = parser.add_subparsers(required=True)

siq = subparsers.add_parser("siq", description="Perform operations on SIQ (.siq) package",
                            help="Perform operations on SIQ (.siq) package")
siq.add_argument("PATH", type=pathlib.Path, help="Path to SIQ package")

siq_subparsers = siq.add_subparsers(required=True)

siq_info = siq_subparsers.add_parser("query", description="Query info about the package")
siq_info.set_defaults(func=query)

siq_convert = siq_subparsers.add_parser("convert", description="Query info about the package")
siq_convert.add_argument("OUTPUT", type=pathlib.Path, help="Path to save parsed data")
siq_convert.set_defaults(func=convert_siq_jsiq)

jsiq = subparsers.add_parser("jsiq", description="Perform operations on JSIQ (.jsiq.zip) package",
                            help="Perform operations on JSIQ (.jsiq.zip) package")
jsiq.add_argument("PATH", type=pathlib.Path, help="Path to JSIQ package")

jsiq_subparsers = jsiq.add_subparsers(required=True)

# jsiq_info = jsiq_subparsers.add_parser("query", description="Query info about the package")
# jsiq_info.set_defaults(func=query)

jsiq_convert = jsiq_subparsers.add_parser("convert", description="Query info about the package")
jsiq_convert.add_argument("OUTPUT", type=pathlib.Path, help="Path to save parsed data")
jsiq_convert.set_defaults(func=convert_jsiq_siq)


def main():
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
