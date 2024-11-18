import platform

import inject

from kindle2pdf.model.page_writer import OutputFormat


class Kindle2PdfApp:

    @inject.autoparams()
    def __init__(self):
        pass

    def run(self, app_name: str, direction: str, save_format: str):

        if not OutputFormat.validate(save_format):
            print(f"Invalid save format: {save_format}")
            return

        save_format = OutputFormat.from_str(save_format)

        # Win or Mac
        if platform.system() == "Windows":
            from kindle2pdf.model.capture_service_win import CaptureControllerForWin
            controller = CaptureControllerForWin(app_name, direction, save_format)

        elif platform.system() == "Darwin":
            from kindle2pdf.model.capture_service_mac import CaptureControllerForMac
            controller = CaptureControllerForMac(app_name, direction, save_format)
        else:
            raise Exception("Unsupported OS")

        controller.run()
