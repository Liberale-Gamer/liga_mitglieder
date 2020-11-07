import getpass, imaplib, email
from email.header import decode_header
from bs4 import BeautifulSoup

def get_mail(id, redact = False):
    M = imaplib.IMAP4()
    M.login("mitgliedsantrag@liberale-gamer.gg", "87_rzb5Z")
    M.select()
    typ, data = M.search(None, 'Subject', str(id))
    typ, data = M.fetch(data[0].split()[-1], '(RFC822)')
    msg = email.message_from_string(data[0][1].decode('utf-8'))

    for part in msg.walk():
        if part.get_content_type() == "text/html":
            body = part.get_payload(decode=False)
        else:
            continue

    M.close()
    M.logout()

    body = BeautifulSoup(body, features="html.parser").get_text(separator="\n")

    if redact:
        body = body.replace("E-Mail: \n", "E-Mail: ")
        body_redacted = ""
        to_be_redacted = ["E-Mail", "Straße", "Telefonnummer"]
        for line in body.splitlines(True):
            if line[:line.find(':')] not in to_be_redacted:
                body_redacted += line
    return body


def get_subjects():
    M = imaplib.IMAP4()
    M.login("mitgliedsantrag@liberale-gamer.gg", "87_rzb5Z")
    M.select()
    typ, data = M.search(None, 'Subject', '[ID ')
    subjects = []
    for num in data[0].split():
        typ, data = M.fetch(num, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1].decode('utf-8'))
                subjects.append(decode_header(msg['subject'])[0][0].decode('utf-8').replace('Liberale Gamer – Mitgliedsantrag von ', ''))
    return subjects
