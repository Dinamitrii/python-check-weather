import segno


def link_to_qr_code(link):
    # link make to qr here
    qr_code = segno.make(link)
    qr_code.save('static/images/qr/qr_code.png', scale=4)
