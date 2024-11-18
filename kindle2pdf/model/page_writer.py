from abc import ABC, abstractmethod
from enum import Enum
import os
from pathlib import Path

import cv2
from PIL import Image
from pdfrw import PdfReader, PdfWriter


class OutputFormat(Enum):

    PNG = "png"
    JPG = "jpg"
    BMP = "bmp"
    PDF = "pdf"

    @classmethod
    def from_str(cls, format_str: str):
        if format_str == "png":
            return cls.PNG
        if format_str == "jpg":
            return cls.JPG
        if format_str == "bmp":
            return cls.BMP
        if format_str == "pdf":
            return cls.PDF
        raise ValueError(f"Invalid format: {format_str}")

    @classmethod
    def validate(cls, format_str: str):
        if format_str not in ["png", "jpg", "bmp", "pdf"]:
            return False, f"Invalid format: {format_str}"
        return True, ""

    def to_str(self):
        return self.value

    def is_image(self):
        return self in [self.PNG, self.JPG, self.BMP]


class CaptureWriter(ABC):

    @abstractmethod
    def save(self, img, basename: str):
        pass

    @abstractmethod
    def handle_finish(self):
        pass


class ImageWriter(CaptureWriter):

    DefaultDir = Path("dist/images")

    def __init__(self, format_str: OutputFormat):
        assert format_str.is_image()
        self.format = format_str

    def get_ext(self):
        return self.format.to_str()

    def create_path(self, basename: str):
        return self.DefaultDir.joinpath(f"{basename}.{self.get_ext()}")

    def save(self, img, basename: str):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pillow = Image.fromarray(img)
        save_path = self.create_path(basename)
        self._save_as_image(save_path, img_pillow)

    def _save_as_image(self, path: Path, img_pillow: Image):
        # 現在のディレクトリを取得
        current_dir = Path.cwd()
        path = current_dir.joinpath(path)
        path.parent.mkdir(exist_ok=True, parents=True)
        # Pillowを使って保存
        if self.format == OutputFormat.PNG:
            img_pillow.save(str(path), "PNG", quality=100)
        elif self.format == OutputFormat.JPG:
            img_pillow.save(str(path), "JPEG", quality=100)
        elif self.format == OutputFormat.BMP:
            img_pillow.save(str(path), "BMP", quality=100)
        else:
            raise ValueError(f"Invalid format: {self.format}")
        print(f"Image saved to {path}")

    def handle_finish(self):
        pass


class PDFWriter(CaptureWriter):

    def __init__(self):
        self.cache_dir_path = Path(".cache_pdf")
        if not self.cache_dir_path.is_dir() or not self.cache_dir_path.exists():
            self.cache_dir_path.mkdir()

    def save(self, img, basename: str):
        filename = basename + ".pdf"
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pillow = Image.fromarray(img)
        save_path = self.cache_dir_path.joinpath(filename)
        # Pillowを使ってPDFとして保存
        img_pillow.save(str(save_path), "PDF", quality=100)

    def handle_finish(self):
        # すべてのPDFを統合
        save_path = Path(os.path.join("dist", "result.pdf"))
        save_path.parent.mkdir(exist_ok=True, parents=True)
        self.merge(save_path)
        # 後処理
        self.close()
        print(f"PDF saved to {save_path}")

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
