import smtplib, ssl
from email.message import Message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import Parser

port = 465  # For SSL
mail_server = "liberale-gamer.gg"
login = "reset@liberale-gamer.gg"
password = "ij2kh4bFgQaq"

def send_email(sender, receiver, subject, text):
	message = MIMEMultipart('alternative')
	message['from'] = sender
	message['to'] = receiver
	message['Subject'] = subject
	text = MIMEText(text, 'plain')
	message.attach(text)

	# Create a secure SSL context
	context = ssl.create_default_context()

	with smtplib.SMTP_SSL(mail_server, port, context=context) as server:
	    server.login(login, password)
	    server.ehlo()

	    server.send_message(message)
	    
if __name__ == '__main__':
#Beispielmail

    sender = "LiGa Mitgliederdatenbank <reset@liberale-gamer.gg>"
    receiver = "communicationbel@gmail.com"
    subject = "Testbetreff"
    text = """\
Subject: Hi there

This message is sent from Python."""

    send_email(sender, receiver, subject, text)
