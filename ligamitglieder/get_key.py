import passwords
from telnetlib import Telnet

def get(oldtoken=None):
    loginstring = 'login serveradmin ' + passwords.ts3 + '\n'
    if oldtoken != None:
        tokendelete = 'tokendelete token=' + oldtoken + '\n'
    with Telnet('localhost', 10011) as tn:
        tn.write(loginstring.encode('utf-8'))
        tn.write("use sid=1\n".encode('utf-8'))
        if oldtoken != None:
            tn.write(tokendelete.encode('utf-8'))
        tn.write("tokenadd tokentype=0 tokenid1=9 tokenid2=0\n".encode('utf-8'))
        pre_response = tn.read_until(b'token=', 5)
        response = tn.read_until(b'\n', 5)
    return response.decode('utf-8')[:-1]

def delete(oldtoken):
    loginstring = 'login serveradmin ' + passwords.ts3 + '\n'
    tokendelete = 'tokendelete token=' + oldtoken + '\n'
    with Telnet('localhost', 10011) as tn:
        tn.write(loginstring.encode('utf-8'))
        tn.write("use sid=1\n".encode('utf-8'))
        tn.write(tokendelete.encode('utf-8'))
