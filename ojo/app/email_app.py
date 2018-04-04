#!/usr/bin/env python3

import logging


import os
import smtplib
import mimetypes

from argparse import ArgumentParser

from email.message import EmailMessage
from ojo.config import config as ojo_config


def read_args(config):
    parser = ArgumentParser(description="""
        Send the contents of a directory as a MIME message.
        Unless the -o option is given, the email is sent by forwarding to configured 
        SMTP server, which then does the normal delivery process.  Your local machine
        must be running an SMTP server.
        """)
    parser.add_argument('-d', '--directory',
                        help="""Mail the contents of the specified directory,
                            otherwise use the directory from config is used.  Only the regular
                            files in the directory are sent, and we don't recurse to
                            subdirectories.""")
    parser.add_argument('-o', '--output',
                        help="""Print the composed message to stdout instead of
                            sending the message to the SMTP server.""",
                        action="store_true",
                        )
    parser.add_argument('-f', '--from_address',
                        help='The value of the From: header')
    parser.add_argument('-t', '--to_address',
                        dest='to_address',
                        help='A To: header value (at least one required)')
    parser.add_argument('-p', '--password',
                        required=True,
                        metavar='PASSWORD',
                        dest='password',
                        help='A password for email login')

    args = parser.parse_args()

    config['echo'] = "True" if getattr(args, 'output') else ""
    for attr in ('directory', 'from_address', 'to_address', 'password'):
        if getattr(args, attr):
            config[attr] = getattr(args, attr)

    return config


def message_factory(config):
    email_from, email_to = config["from_address"], config["to_address"]

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


def setup_echo_sender(config):
    from_address, to_address = config["from_address"], config["to_address"]
    msg = "----- To : %s -----\n ----- From : %s ----- \n %s \n\n"

    def send_message(message):
        print(msg % (from_address, to_address, message.as_string()))

    def close():
        pass

    return send_message, close


def setup_email_sender(config):
    server_address, server_port = config["server_address"], config["server_port"]
    from_address, to_address = config["from_address"], config["to_address"]
    password = config["password"]

    server = smtplib.SMTP(server_address, server_port)
    server.starttls()
    server.login(from_address, password)

    def send_message(message):
        server.sendmail(from_address, to_address, message.as_string())

    def close():
        server.quit()

    return send_message, close


def setup_sender(config):
    if config["echo"]:
        return setup_echo_sender(config)
    else:
        return setup_email_sender(config)


def read_file_paths(conf):
    file_path = conf["directory"]

    if os.path.isfile(file_path):
        files = (file_path, )
    else:
        files = (
            os.path.join(file_path, f) for f in os.listdir(file_path)
        )
    return (f for f in files if is_file_to_upload(f))


def is_file_to_upload(file_path):
    ctype, _ = mimetypes.guess_type(file_path)
    return ctype in ("image/jpeg", )


if __name__ == "__main__":
    conf = ojo_config.load()["email_app"]

    args = read_args(conf)

    logging.info("working with config %s" % dict(conf))

    factory = message_factory(conf)
    sender, cleanup = setup_sender(conf)

    files_paths = read_file_paths(conf)

    for file_path in files_paths:
        try:
            sender(factory(file_path))
        except Exception as e:
            logging.warning("Failed to send message from %s" % file_path, e)

    cleanup()




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