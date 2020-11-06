import getpass, imaplib, email
from bs4 import BeautifulSoup

def getmail(id):

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
    return BeautifulSoup(body, features="html.parser").get_text(separator="\n")
