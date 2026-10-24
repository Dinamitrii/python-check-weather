import segno


def link_to_qr_code(link: str) -> str:
    """Return the QR code for *link* as a PNG data URI (nothing is written to disk)."""
    return segno.make(link).png_data_uri(scale=4)
