from sbomber.output import generate_output
from sbomber.error import SbomberError
from sbomber.parser import parse
from sbomber.zensical_config import generate_config

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from functools import partial
import shutil
from multiprocessing import Process
import os

import zensical

ZENSICAL_MARKDOWN_DIR = "docs"
ZENSICAL_SITE_DIR = "site"


def main():
    with TemporaryDirectory() as tmp:
        # define absolute paths to important zensical directories
        zensical_site_path = Path(tmp) / ZENSICAL_SITE_DIR
        zensical_docs_path = Path(tmp) / ZENSICAL_MARKDOWN_DIR
        zensical_config_path = Path(tmp) / "zensical.toml"

        # tell dag-viewer where to output it assets
        os.environ["DAG_VIEWER_SITE_DIR"] = str(zensical_site_path)

        # generate the zensical config
        generate_config(zensical_config_path)

        # parse the arguments
        p = argparse.ArgumentParser(prog="sbomber")
        p.add_argument("filepath", help="Filepath to sbom", type=Path)
        p.add_argument(
            "--markdown",
            "-m",
            help="Output intermediate markdown to provided directory",
            type=Path,
            default=None,
        )
        p.add_argument(
            "--output",
            "-o",
            help="Output directory for html",
            type=Path,
            default=Path("site"),
        )
        p.add_argument(
            "--serve",
            "-s",
            help="Serve generated site at localhost on provided port",
            type=int,
            default=False
        )
        args = p.parse_args()

        # parse the sbom and genrate the markdown
        try:
            document = parse(args.filepath)
        except SbomberError as e:
            print(f"ERROR: {e}")
        generate_output(document, zensical_docs_path)

        # use zensical to turn markdown into html
        # need to run zensical in its own process since dag-viewer macro uses atexit
        # to copy its assets into the site directory
        build = partial(
            zensical.build, str(zensical_config_path), {"clean": True, "strict": False}
        )
        p = Process(target=build)
        p.start()
        p.join()

        # copy generated files to output dirs
        for p in [args.output, args.markdown]:
            if p is None:
                continue
            if p.is_dir():
                shutil.rmtree(p)
            shutil.copytree(zensical_site_path, p)

    # serve the site
    if args.serve:
        Handler = partial(SimpleHTTPRequestHandler, directory=args.output)
        with TCPServer(("", args.serve), Handler) as httpd:
            print(f"Serving on http://localhost:{args.serve}")
            httpd.serve_forever()


if __name__ == "__main__":
    main()
