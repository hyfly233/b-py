import os

import fitz  # PyMuPDF
from PIL import Image
from dotenv import load_dotenv

load_dotenv()


def main():
    pdf_path = os.getenv('PDF_PATH')
    page_number = 0  # 第1页，0为起始
    rect = (100, 100, 400, 300)  # (x0, y0, x1, y1) 左上和右下坐标

    # 打开PDF
    doc = fitz.open(pdf_path)
    page = doc[page_number]

    # 截图区域
    clip = fitz.Rect(rect)
    pix = page.get_pixmap(clip=clip, dpi=200)  # 可调整dpi提高清晰度

    # 保存为图片
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.save("screenshot.png")
    print("截图已保存为 screenshot.png")


if __name__ == '__main__':
    main()
