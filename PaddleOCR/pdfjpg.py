from pdf2image import convert_from_path


def pdf_to_jpg(pdf_path, output_dir, dpi=300):

    pages = convert_from_path(pdf_path, dpi=dpi)

    for i, page in enumerate(pages):
        output_path = f"{output_dir}/page_{i + 1}.jpg"
        page.save(output_path, "JPEG")


# 使用示例
pdf_to_jpg("input.pdf", "output_dir")