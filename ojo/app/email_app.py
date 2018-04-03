import smtplib
from email.message import EmailMessage

import os
import smtplib
# For guessing MIME type based on file name extension
import mimetypes

from argparse import ArgumentParser

from email.message import EmailMessage
from email.policy import SMTP


def message_factory(email_to, email_from):
    def new_message(file_path):
        msg = EmailMessage()
        msg['To'] = email_to
        msg['From'] = email_from

        file_name = os.path.basename(file_path)
        msg['Subject'] = "Sending %s" % os.path.basename(file_path)

        ctype, encoding = mimetypes.guess_type(file_path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            maintype, subtype = "application", "octet-stream"
        else:
            maintype, subtype = ctype.split('/', 1)

        abs_path = os.path.abspath(file_path)
        with open(abs_path, 'rb') as fp:
            msg.add_attachment(
                fp.read(),
                maintype=maintype,
                subtype=subtype,
                filename=file_name
            )
        return msg

    return new_message


def setup_email_server(info):
    pass


def send_emails(email_server, directory, message_factory):
    pass


if __name__ == "__main__":
    factory = message_factory(
        email_from="ofres@email.com",
        email_to="sharoffer@email.com",
    )
    msg = factory("/Users/osharabi/Pictures/my5/IMG_2142.jpg")
    print(msg)

# fromaddr = "YOUR ADDRESS"
# toaddr = "ADDRESS YOU WANT TO SEND TO"
# msg = EmailMessage()
# msg['From'] = fromaddr
# msg['To'] = toaddr
# msg['Subject'] = "SUBJECT OF THE MAIL"
#
# body = "YOUR MESSAGE HERE"
# msg.attach(MIMEText(body, 'plain'))

# server = smtplib.SMTP('smtp.gmail.com', 587)
# server.starttls()
# server.login(fromaddr, "YOUR PASSWORD")
# text = msg.as_string()
# server.sendmail(fromaddr, toaddr, text)
# server.quit()