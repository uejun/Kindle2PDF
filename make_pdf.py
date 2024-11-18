import os
import platform
import click


@click.command()
@click.option('--name', '-n', type=str, default='Kindle', help="application name")
@click.option('--direction', '-d', type=str, default='right', help="paging direction")
def main(name, direction):
    # Mac Winで切り替え
    if platform.system() == 'Darwin':
        from controller_mac import CaptureController
    elif platform.system() == 'Windows':
        from controller_win import CaptureController
    else:
        raise ValueError("Unsupported OS")
    controller = CaptureController(name, direction)
    controller.start()


if __name__ == '__main__':
    main()