from __future__ import annotations

import argparse
import pathlib

from sigame_tools.datatypes import SIDocument, SIDocumentTypes


def guess_type(file: str | pathlib.Path) -> str:
    if isinstance(file, pathlib.Path):
        file: str = file.name
    if file.endswith(".jsiq.zip"):
        return SIDocumentTypes.JSIQ
    if file.endswith(".siq"):
        return SIDocumentTypes.SIQ
    return ""


def query(args):
    src = args.src
    input_type = args.in_type or guess_type(src)
    if not input_type:
        raise ValueError(f"Unable to guess type for file {src}")
    si_doc: SIDocument = SIDocument.read_as(src, input_type)
    print(si_doc.package)


def convert(args):
    src: pathlib.Path = args.src
    if src.is_dir():
        raise ValueError(f"'{src}' is a Directory")
    dst: pathlib.Path = args.dst
    input_type = args.in_type or guess_type(src)
    output_type = "" if dst.is_dir() else args.out_type or guess_type(dst)
    if not input_type:
        raise ValueError(f"Unable to guess type for input file '{src}'")
    if not output_type:
        if dst.is_dir():
            raise ValueError(f"'{dst}' is a Directory, please specify full path or provide file type")
        raise ValueError(f"Unable to guess type for output file '{dst}'")
    print(f"Converting from {input_type} to {output_type} ...")
    si_doc: SIDocument = SIDocument.read_as(src, input_type)
    print("Load successful")
    si_doc.save_as(dst, output_type)
    print("Save successful")


parser = argparse.ArgumentParser(description="SI Game tools CLI")

commands = parser.add_subparsers(required=True, help="Specific action to perform", metavar="<command>")

# Query
query_parser = commands.add_parser("query", description="Query info about SI Game package",
                                   help="Query info about SI Game package")
query_parser.set_defaults(func=query)
query_parser.add_argument("--in-type", "-i", choices=(SIDocumentTypes.SIQ, SIDocumentTypes.JSIQ),
                          help="Explicitly specify input file format")
query_parser.add_argument("src", type=pathlib.Path, help="SI Game package file\n"
                                                         "File format is detected automatically", metavar="FILE")

# Convert
convert_parser = commands.add_parser("convert", description="Convert SI Game package to another format",
                                     help="Convert SI Game package to another format",
                                     formatter_class=argparse.RawTextHelpFormatter)
convert_parser.set_defaults(func=convert)

# src_group = convert_parser.add_argument_group("Source")
convert_parser.add_argument("--in-type", "-i", choices=(SIDocumentTypes.SIQ, SIDocumentTypes.JSIQ),
                            help="Explicitly specify file format")
convert_parser.add_argument("src", type=pathlib.Path, help="Source SI Game package file\n"
                                                           "File format is detected automatically", metavar="SOURCE")

# convert_parser.add_argument("--format", "-f", dest="bar")
# dst_group = convert_parser.add_argument_group("Destination")
convert_parser.add_argument("--out-type", "-o", choices=(SIDocumentTypes.SIQ, SIDocumentTypes.JSIQ),
                            help="Explicitly specify output file format\n"
                                 "(required when DESTINATION is a Directory)")
convert_parser.add_argument("dst", type=pathlib.Path, help="Destination package file or directory\n"
                                                           "File format is detected automatically\n"
                                                           "If directory is specified instead, format is required",
                            metavar="DESTINATION")


def main():
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
