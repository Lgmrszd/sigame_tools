# SI Game tools
Collection of tools to work with SI Game packages

## Installation

```shell
pip install git+https://github.com/Lgmrszd/sigame_tools.git
```

## Usage
### As a module
Submodule `sigame_tools.datatypes` contains [most classes for object used for SIGame](https://github.com/VladimirKhil/SI/blob/master/src/Common/SIPackages)  (Package, Theme, Round etc.) using same structure with few exceptions.

Example of reading game package:

```python
import pathlib
import sigame_tools.datatypes

path = pathlib.Path("path/to/pack.siq")
sigame_tools.datatypes.SIDocument.read_as(path, "siq")
```

### CLI
```shell
$ sigame-tools -h
usage: sigame-tools [-h] <command> ...

SI Game tools CLI

positional arguments:
  <command>   Specific action to perform
    query     Query info about SI Game package
    convert   Convert SI Game package to another format

options:
  -h, --help  show this help message and exit
  


$ sigame-tools convert -h
usage: sigame-tools convert [-h] [--in-type {siq,jsiq.zip}] [--out-type {siq,jsiq.zip}] SOURCE DESTINATION

Convert SI Game package to another format

positional arguments:
  SOURCE                Source SI Game package file
                        File format is detected automatically
  DESTINATION           Destination package file or directory
                        File format is detected automatically
                        If directory is specified instead, format is required

options:
  -h, --help            show this help message and exit
  --in-type {siq,jsiq.zip}, -i {siq,jsiq.zip}
                        Explicitly specify file format
  --out-type {siq,jsiq.zip}, -o {siq,jsiq.zip}
                        Explicitly specify output file format
                        (required when DESTINATION is a Directory)

```
