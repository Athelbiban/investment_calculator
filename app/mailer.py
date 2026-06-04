import imaplib
import email
from pathlib import Path
from typing import Optional
from contextlib import nullcontext
from app.animation import AnimationManager
from app.config import MAIL_PASSWORD, BROKERAGE_ACCOUNT_NUMBER, MAIL_USERNAME, IMAP_SERVER, IMAP_FOLDER
from app.directing import get_directory


def write_broker_reports(imap: imaplib.IMAP4_SSL, directory: str | Path, ext: str ='.html') -> dict[str, int | str]:
    existing_files_set = {f.name for f in Path(directory).iterdir() if f.is_file()}
    updated_count = 0

    status, data = imap.search(None, 'ALL')
    if status != 'OK': return {
        'updated_count': 0,
        'total_amount_files': len(existing_files_set),
        'message': "Запись файлов отчетов отменена. Статус imaplib.IMAP4_SSL отличается от 'OK'"
    }

    for msg_id in data[0].split():
        status, msg_data = imap.fetch(msg_id, '(RFC822)')
        if status != 'OK': continue

        msg = email.message_from_bytes(msg_data[0][1])
        for part in msg.walk():
            if part.get_content_disposition() != 'attachment': continue

            fname = part.get_filename()
            if not fname or (BROKERAGE_ACCOUNT_NUMBER and not fname.startswith(BROKERAGE_ACCOUNT_NUMBER)): continue
            if not fname.lower().endswith(ext): continue
            if fname in existing_files_set: continue

            payload = part.get_payload(decode=True)
            if isinstance(payload, bytes):
                Path(directory, fname).write_bytes(payload)
                existing_files_set.add(fname)
                updated_count += 1

    return {
        'updated_count': updated_count,
        'total_amount_files': len(existing_files_set),
        'message': "Успешно"
    }

def _get_credential(config_val: Optional[str], prompt: str, anim: Optional[AnimationManager]) -> str:
    if config_val: return config_val
    context = anim.paused() if anim else nullcontext()
    with context:
        return input(prompt)

def get_reports(animation: Optional[AnimationManager] = None) -> dict[str, int | str]:
    mail_password = _get_credential(MAIL_PASSWORD, 'MAIL_PASSWORD: ', animation)
    mail_username = _get_credential(MAIL_USERNAME, 'USERNAME: ', animation)

    imap = imaplib.IMAP4_SSL(IMAP_SERVER)
    try:
        imap.login(mail_username, mail_password)
        imap.select(IMAP_FOLDER)
        result = write_broker_reports(imap, get_directory())
        return result
    finally:
        try:
            imap.logout()
        except imaplib.IMAP4.error:
            pass



if __name__ == '__main__':
    get_reports()
