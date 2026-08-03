from sbomber.output import generate_output
from sbomber.error import SbomberError
from sbomber.parser import parse

import argparse
from pathlib import Path

p = argparse.ArgumentParser(prog="sbomber")
p.add_argument("filepath", help="filepath to sbom", type=Path)
p.add_argument("--output", "-o", help="output directory", type=Path, default=Path("output"))

args = p.parse_args()

try: 
    document = parse(args.filepath)
except SbomberError as e:
    print(f"ERROR: {e}")

generate_output(document, args.output)
