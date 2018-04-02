# coding: utf-8
from email.mime.image import MIMEImage


def add_email_embed_image(email, img_content_id, img_data):
    """
    https://docs.python.org/3.5/library/email-examples.html
    """
    img = MIMEImage(img_data)
    img.add_header('Content-ID', '<%s>' % img_content_id)
    img.add_header('Content-Disposition', 'inline')
    email.attach(img)