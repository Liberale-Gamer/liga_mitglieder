import smtplib, ssl
from email.message import Message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import Parser
import passwords

port = 465  # For SSL
mail_server = "liberale-gamer.gg"
login = "intern@liberale-gamer.gg"
password = passwords.mail_intern

def send_email(sender_name, receiver, subject, text, replyto=None):
	message = MIMEMultipart('alternative')
	message['from'] = sender_name + " <" + login + ">"
	message['to'] = receiver
	if replyto != None:
		message['reply-to'] = replyto
	message['Subject'] = subject
	text = MIMEText(text, 'html')
	message.attach(text)

	# Create a secure SSL context
	context = ssl.create_default_context()

	with smtplib.SMTP_SSL(mail_server, port, context=context) as server:
	    server.login(login, password)
	    server.ehlo()

	    server.send_message(message)
	    
