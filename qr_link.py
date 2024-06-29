import segno


def qr_link(link):
    # link from where here
    link = link.replace(' ', '+')
    qr = segno.make(link)
    qr.save('static/images/qr/qr_link.png', scale=2)
