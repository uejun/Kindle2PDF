import click

from controller import CaptureController


@click.command()
@click.option('--name', '-n', type=str, default='Kindle', help="application name")
@click.option('--direction', '-d', type=str, default='right', help="paging direction")
def main(name, direction):
    controller = CaptureController(name, direction)
    controller.start()


if __name__ == '__main__':
    main()