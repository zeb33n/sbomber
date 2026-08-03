from sbomber.todot import todot
from sbomber.error import SbomberError
from sbomber.parser import parse

import argparse
from pathlib import Path

p = argparse.ArgumentParser(prog="sbomber")
p.add_argument("filepath", help="filepath to sbom", type=Path)

args = p.parse_args()

try: 
    document = parse(args.filepath)
except SbomberError as e:
    print(f"ERROR: {e}")

print(todot(document))
