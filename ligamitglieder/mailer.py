import smtplib, ssl
from email.message import Message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import Parser
import passwords

port = 465  # For SSL
mail_server = "liberale-gamer.gg"
login = "reset@liberale-gamer.gg"
password = passwords.reset

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
	    