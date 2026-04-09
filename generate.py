import uuid
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
import qrcode

from niimprint import SerialTransport, PrinterClient


def uuid7():
    ts_ms = int(datetime.utcnow().timestamp() * 1000)
    rand = uuid.uuid4().int & ((1 << 74) - 1)

    value = (ts_ms << 74) | rand
    value &= ~(0xF << 76)
    value |= (0x7 << 76)
    value &= ~(0x3 << 62)
    value |= (0x2 << 62)

    return uuid.UUID(int=value)


def split_uuid(u):
    s = str(u)
    return s[:18], s[18:]  # 18 + 18 chars


def create_label(u, path="/tmp/label.png"):
    line1, line2 = split_uuid(u)
    full = str(u)

    width, height = 475, 120
    img = Image.new("1", (width, height), 1)
    draw = ImageDraw.Draw(img)

    # --- QR ---
    qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=0,
            )
    qr.add_data(full)
    qr.make()
    qr_img = qr.make_image(fill_color="black", back_color="white")
    img.paste(qr_img, (10, 0))

    # --- TEXT ---
    try:
        font = ImageFont.truetype("./BebasNeue-Regular.ttf", 50)
    except:
        font = ImageFont.load_default()

    text_x = 130

    # vertical centering for 2 lines
    line_spacing = 6
    bbox1 = draw.textbbox((0, 0), line1, font=font)
    bbox2 = draw.textbbox((0, 0), line2, font=font)

    total_h = (bbox1[3] - bbox1[1]) + (bbox2[3] - bbox2[1]) + line_spacing
    start_y = (height - total_h) // 2 - 10

    draw.text((text_x, start_y), line1, fill=0, font=font)
    draw.text((text_x, start_y + (bbox1[3] - bbox1[1]) + line_spacing), line2, fill=0, font=font)

    img.save(path)
    return path


def print_label(path):
    transport = SerialTransport(port="/dev/ttyACM0")
    printer = PrinterClient(transport)

    image = Image.open(path)

    # equivalent to -r 90
    image = image.rotate(-90, expand=True)

    printer.print_image(image, density=3)


if __name__ == "__main__":
    u = uuid7()
    print("UUIDv7:", u)

    path = create_label(u)
    print("Saved:", path)

    print_label(path)
