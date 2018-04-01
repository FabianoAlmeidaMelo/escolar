# coding: utf-8
from email.mime.image import MIMEImage


def add_email_embed_image(email, img_content_id, img_data):
    """
    email is a django.core.mail.EmailMessage object
    """
    img = MIMEImage(img_data)
    img.add_header('Content-ID', '<%s>' % img_content_id)
    img.add_header('Content-Disposition', 'inline')
    email.attach(img)