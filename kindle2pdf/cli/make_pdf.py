import os
from pathlib import Path
import platform
import sys

import click
import inject

PROJECT_HOME_DIR = Path(os.path.abspath(__file__)).parent.parent.parent
assert PROJECT_HOME_DIR.exists()
sys.path.append(str(PROJECT_HOME_DIR))


def configure(binder):
    pass


@click.command()
@click.option('--name', '-n', type=str, default='Kindle', help="application name")
@click.option('--direction', '-d', type=str, default='right', help="paging direction")
@click.option('--save_format', '-f', type=click.Choice(['png', 'jpg', 'bmp', 'pdf']), default='pdf')
def main(name, direction, save_format: str):
    from kindle2pdf.app.kindle2pdf_app import Kindle2PdfApp
    app = Kindle2PdfApp()
    app.run(name, direction, save_format)


if __name__ == '__main__':
    inject.configure(configure)
    main()
