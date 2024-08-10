import segno


def generate_qr(link):

    link = segno.make(link)
    link.save('static/images/qr/qr_code.png', scale=4)
