import os
from pathlib import Path

import cv2
from PIL import Image
from pdfrw import PdfReader, PdfWriter


class PDFWriter(object):

    def __init__(self):
        self.cache_dir_path = Path(".cache_pdf")
        if not self.cache_dir_path.is_dir() or not self.cache_dir_path.exists():
            self.cache_dir_path.mkdir()

    def save_as_pdf(self, img, filename):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pillow = Image.fromarray(img)
        save_path = self.cache_dir_path.joinpath(filename)
        # Pillowを使ってPDFとして保存
        img_pillow.save(str(save_path), "PDF", quality=100)

    def merge(self, save_path: Path):
        writer = PdfWriter()

        pdf_numbers = [int(path.stem)
                       for path in self.cache_dir_path.glob("*.pdf")]

        pdf_paths = [self.cache_dir_path.joinpath(str(pdf_num) + '.pdf')
                     for pdf_num in sorted(pdf_numbers)]

        for pdf_path in pdf_paths:
            writer.addpages(PdfReader(pdf_path).pages)

        writer.write(str(save_path))

    def close(self):
        for path in self.cache_dir_path.glob("*.pdf"):
            os.remove(path)
