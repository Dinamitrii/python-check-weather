import segno


def generate(link):

    link = segno.make(link)
    link.save('static/images/qr/qr_code.png', scale=6)
