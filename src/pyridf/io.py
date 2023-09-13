
from .ridf import ridf
from . import element
from .parser import parser


def read(fpath, maxblock=None):
    with open(fpath, "rb") as f:
        print(f.name)
        ridf_parser = parser()
        content = f.read()
        return ridf_parser.parse(content, maxblock)


def write(fpath, data:ridf):
    with open(fpath, "wb") as f:
        f.write(data.encode())

