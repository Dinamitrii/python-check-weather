import segno


def generate(url):

    link_to_qr = segno.make('URL')
    link_to_qr.save('static/images/qr/qr_link.png', scale=5)
