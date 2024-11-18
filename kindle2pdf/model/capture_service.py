from .page_writer import PDFWriter, ImageWriter, CaptureWriter, OutputFormat


class CaptureServiceBase:

    def __init__(self, app_name, direction, save_format: OutputFormat):
        self.app_name = app_name
        self.direction = direction
        self.save_format = save_format
        if save_format == OutputFormat.PDF:
            self.writer: CaptureWriter = PDFWriter()
        else:
            self.writer: CaptureWriter = ImageWriter()
        self.pager = None

        self.MAX_PAGE = 3000

    def run(self):
        raise NotImplementedError
