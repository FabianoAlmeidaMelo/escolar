# coding: utf-8
import smtplib  
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from escolar import settings


def send_email(recipient, subject, txt_message='', html_message='', sendername=None):
    '''
    AWS Simple Email Service
    https://docs.aws.amazon.com/pt_br/ses/latest/DeveloperGuide/examples-send-using-smtp.html

    Passe o argumento message formatado
    '''

    RECIPIENT  = recipient

    HOST = settings.HOST
    PORT = settings.PORT
    SUBJECT = subject

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = (
        "{message}"
        "Smart Is Cool\r\n"
        "sistema de gestão escolar"
    ).format(message=txt_message)


    # The HTML body of the email.
    BODY_HTML = ("""<html>
    <head></head>
    <body>
      {html_message}  
      <h5>Smart Is Cool</h5>
      <p><small>Sistema de Gestão Escolar</small></p>
    </body>
    </html>
    """).format(html_message=html_message)

    SENDER = settings.SENDER
    SENDERNAME = settings.SENDERNAME
    if sendername:
        SENDERNAME = sendername
    USERNAME_SMTP = settings.USERNAME_SMTP
    PASSWORD_SMTP = settings.PASSWORD_SMTP

    # Create message container - the correct
    # MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
    msg['To'] = RECIPIENT

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(BODY_TEXT, 'plain')
    part2 = MIMEText(BODY_HTML, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    try:  
        server = smtplib.SMTP(HOST, PORT)
        server.ehlo()
        server.starttls()
        #stmplib docs recommend calling ehlo() before & after starttls()
        server.ehlo()
        server.login(USERNAME_SMTP, PASSWORD_SMTP)
        server.sendmail(SENDER, RECIPIENT, msg.as_string())
        server.close()

    except Exception as e:
        print ("Error: ", e)
    else:
        print ("Email sent!")