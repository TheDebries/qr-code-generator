from qrcodegen import QrCode
from PIL import Image, ImageDraw
from math import floor
# url = "https://forms.gle/XumVzPv7caGi3E6G6"
# name = "Call_of_Cthulhu_QR_code_large"
# corner_x, corner_y = (1180, 1190)
# size = 1080


# def from_url(url: str, filename: str):
#     qrc = QrCode.encode_text(url, QrCode.Ecc.LOW)
#     to_image(qrc, filename)
#     pass


def print_qr(qrcode: QrCode) -> None:
    """Prints the given QrCode object to the console."""
    border = 4
    for y in range(-border, qrcode.get_size() + border):
        for x in range(-border, qrcode.get_size() + border):
            print("\u2588 "[1 if qrcode.get_module(x, y) else 0] * 2, end="")
        print()
    print()


def to_image(qrcode: QrCode, filename: str, template: str, size: int, corner_x: int, corner_y: int) -> None:
    img = Image.open(template).convert("RGBA")
    dr = ImageDraw.Draw(img)
    dpixel = floor(size / qrcode.get_size())

    def to_rectangle(x, y):
        xb = corner_x + dpixel * x
        yb = corner_y + dpixel * y
        return (xb, yb, xb + dpixel, yb + dpixel)

    for x in range(qrcode.get_size()):
        for y in range(qrcode.get_size()):
            if qrcode.get_module(x, y):
                dr.rectangle(xy=to_rectangle(x, y), fill=(0, 0, 0), width=0)

    img.save(filename, "PNG", quality=300)


# if __name__ == "__main__":
#     from_url(url, name)
