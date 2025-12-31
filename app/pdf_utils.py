import fitz  # PyMuPDF
from PIL import Image
import io

def apply_stamp(pdf_path, seal_path, sign_path, output_path):
    doc = fitz.open(pdf_path)
    page = doc[0]  # first page

    # Flatten PDF → image
    zoom = 2
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)

    page_img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGBA")

    # Load images
    seal = Image.open(seal_path).convert("RGBA")
    sign = Image.open(sign_path).convert("RGBA")

    # Resize seal
    seal_width = int(page_img.width * 0.22)
    seal = seal.resize((seal_width, seal_width))

    # Resize signature (wider, not square)
    sign_width = int(page_img.width * 0.35)
    sign_height = int(sign_width * 0.35)
    sign = sign.resize((sign_width, sign_height))

    # Positions
    margin = 50

    seal_x = page_img.width - seal.width - margin
    seal_y = page_img.height - seal.height - margin

    sign_x = page_img.width - sign.width - margin
    sign_y = seal_y + seal.height + 10  # below seal

    # Paste signature first, then seal
    page_img.paste(sign, (sign_x, sign_y), sign)
    page_img.paste(seal, (seal_x, seal_y), seal)

    # UI positioning = simple math
    # Smaller y → goes up
    # Bigger y → goes down

    # Create new PDF
    new_doc = fitz.open()
    new_page = new_doc.new_page(
        width=page_img.width,
        height=page_img.height
    )

    img_bytes = io.BytesIO()
    page_img.save(img_bytes, format="PNG")

    new_page.insert_image(
        new_page.rect,
        stream=img_bytes.getvalue()
    )

    new_doc.save(output_path)
    doc.close()
    new_doc.close()
