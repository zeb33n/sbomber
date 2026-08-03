from sbomber.parser import Document, parse

import argparse
from pathlib import Path

p = argparse.ArgumentParser(prog="sbomber")
p.add_argument("filepath", help="filepath to sbom", type=Path)
args = p.parse_args()

print(parse(args.filepath))
