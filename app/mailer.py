import imaplib
import email
import base64
import re
import passwd.config_mail as dt

from app.directing import get_directory
from app.animation import start_animation_func, stop_animation_func


def write_broker_reports(imap, directory, files_extension='.html'):

    id_list = imap.search(None, 'ALL')[1][0].split()
    for next_mail_id in id_list:

        res, data = imap.fetch(next_mail_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        for part in msg.walk():

            if part.get_content_disposition() == 'attachment'\
                    and part.get_filename()[:7] == dt.BROKERAGE_ACCOUNT_NUMBER\
                    and (re.search(r'\.\w+$', part.get_filename()).group() == files_extension
                         or re.search(r'\.\w+$', part.get_filename()).group() == files_extension.upper()):

                with open(f'{directory}{part.get_filename()}', 'w', encoding='utf-8') as ouf:
                    ouf.write(base64.b64decode(part.get_payload()).decode())


def get_reports():

    if dt.MAIL_PASS:
        mail_pass = dt.MAIL_PASS
    else:
        stop_animation_func()
        mail_pass = input('MAIL_PASS: ')
        start_animation_func()

    if dt.USERNAME:
        username = dt.USERNAME
    else:
        stop_animation_func()
        username = input('USERNAME: ')
        start_animation_func()

    directory = get_directory()
    imap_server = 'imap.mail.ru'
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(username, mail_pass)
    imap.select('SberBroker')
    write_broker_reports(imap, directory)


if __name__ == '__main__':
    get_reports()
