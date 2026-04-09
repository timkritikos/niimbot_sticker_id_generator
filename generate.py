import uuid6
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
import qrcode

from niimprint import SerialTransport, PrinterClient

import argparse

def uuid7():

    return uuid6.uuid7()


def split_uuid(u):
    s = str(u)
    return s[:18], s[18:]  # 18 + 18 chars


def create_label(uuid, title, path="label.png"):
    line1, line2 = split_uuid(uuid)
    full = str(uuid)

    width, height = 475, 120
    img = Image.new("1", (width, height), 1)
    draw = ImageDraw.Draw(img)

    # --- QR ---
    qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=4,
            border=0,
            )
    qr.add_data(full)
    qr.make()
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("1")
    img.paste(qr_img, (10, 2))

    # --- TEXT ---
    codefont = ImageFont.truetype("BebasNeue-Regular.ttf", 48)
    textfont = ImageFont.truetype("PatrickHand-Regular.ttf", 37)

    text_x = 133

    _, _, w, _ = draw.textbbox((0, 0), title , font=textfont)
    draw.text(((width-133-w)/2+133, -10), title, font=textfont, fill=0)

    # vertical centering for 2 lines
    line_spacing = 6
    bbox1 = draw.textbbox((0, 0), line1, font=codefont)
    bbox2 = draw.textbbox((0, 0), line2, font=codefont)

    total_h = (bbox1[3] - bbox1[1]) + (bbox2[3] - bbox2[1]) + line_spacing
    start_y = 33

    draw.text((text_x, start_y), line1, fill=0, font=codefont)
    draw.text((text_x, start_y + (bbox1[3] - bbox1[1]) + line_spacing), line2, fill=0, font=codefont)

    img.save(path)
    return path


def print_label(path,serial):
    transport = SerialTransport(port=serial)
    printer = PrinterClient(transport)

    image = Image.open(path)

    # equivalent to -r 90
    image = image.rotate(-90, expand=True)

    printer.print_image(image, density=3)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    prog='Sticker ID Generator',
                    description='Generate ID sticker')
    parser.add_argument('-s', '--serial-port', default="/dev/ttyACM0" )
    parser.add_argument('-t', '--title', default="Scanned photo ID:" )
    parser.add_argument('-v', '--version', action='store_true' )
    args = parser.parse_args()
    
    if args.version == True:
        print("v0.0")
    else:
        u = uuid7()
        print("UUIDv7:", u)

        path = create_label(u,args.title)
        print("Saved:", path)

        print_label(path,args.serial_port)
