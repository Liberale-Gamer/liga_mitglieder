import smtplib, ssl
from email.message import Message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import Parser

port = 465  # For SSL
mail_server = "liberale-gamer.gg"
login = "mitgliedsantrag@liberale-gamer.gg"
password = "87_rzb5Z"

def send_email(sender, receiver, subject, text, replyto=None):
	message = MIMEMultipart('alternative')
	message['from'] = sender
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
	    
# if __name__ == '__main__':
# #Beispielmail

#     sender = "LiGa Mitgliederdatenbank <reset@liberale-gamer.gg>"
#     receiver = "communicationbel@gmail.com"
#     subject = "Testbetreff"
#     text = """\
# Subject: Hi there

# This message is sent from Python.

# Hallo [Vorname],<br /><br />ich bin Marvin von den Liberalen Gamern und möchte dich bei uns herzlich willkommen heißen!<br /><br />Wir haben dich mit den folgenden Daten in unser Mitgliederverzeichnis aufgenommen &ndash; schau einmal, ob alles richtig ist:<br /><br />Vorname: [Vorname]<br />Name: [Name]<br />Anschrift: [Straße]&nbsp;[Hausnummer]<br />PLZ, Ort: [PLZ]&nbsp;[Stadt]<br />E-Mail-Adresse: [E-Mail]<br />Handynummer: [Handynummer]<br />Geburtsdatum: [Geburtsdatum]<br /><br />Mitgliedsnummer: [ID]<br /><br />Hier noch ein paar hilfreiche Links rund um die LiGa:<br /><br />Unsere offiziellen Social-Media-Kanäle (gerne teilen und liken):<br /><a href="https://www.facebook.com/liberalegamer">https://www.facebook.com/liberalegamer</a><br /><a
# href="https://twitter.com/LiberaleGamer">https://twitter.com/LiberaleGamer</a><br /><a href="https://www.instagram.com/LiberaleGamer">https://www.instagram.com/LiberaleGamer</a><br /><br />Unsere verbandsinternen Dokumente wie Beschlüsse, Satzung oder Geschäftsordnung dokumentieren wir in unserem Wiki: <a href="https://wiki.liberale-gamer.gg">https://wiki.liberale-gamer.gg</a><br /><br />Unsere geschlossene Facebook-Gruppe: <a href="https://www.facebook.com/groups/433296140360035/">https://www.facebook.com/groups/433296140360035/</a><br />Unserer geschlossenen WhatsApp-Gruppe kann ich dich hinzufügen, wenn du mir dafür auf WhatsApp eine kurze Nachricht schreibst &ndash; mit <a
# href="https://api.whatsapp.com/send?phone=4917657517450&text=Hallo+Marvin%2C+bitte+f%C3%BCge+mich+der+LiGa-WhatsApp-Gruppe+hinzu%21+urlparse([Vorname])+urlparse([Name])+%28Mitgliedsnummer+[ID]%29%2E%20Ich+bin+damit+einverstanden%2C+dass+mit+Hinzuf%C3%BCgen+in+diese+Gruppe+meine+Handynummer+an+WhatsApp+und+alle+Mitglieder+in+der+Gruppe+weitergegeben+wird%2E">diesem Link</a> geht das ganz einfach. Dazu ein notwendiger Hinweis zum Datenschutz: Wenn du uns mitteilst, dass du zu unserer LiGa-WhatsApp-Gruppe hinzugefügt werden möchtest, erklärst du dich damit einverstanden, dass mit Hinzufügen in diese Gruppe deine Handynummer an WhatsApp und alle Mitglieder in der Gruppe weitergegeben wird.<br /><br />Noch ein kurzer Hinweis zu der WhatsApp-Gruppe: Diese ist ausschließlich für Vereins- und Gaming-Themen gedacht. Du findest in der Gruppenbeschreibung aber auch einen Link zur LiGa-Talk-Gruppe, in der über alles Mögliche diskutiert werden kann. Auch haben wir weitere Gruppen speziell für einzelne Spiele eingerichtet. Eine Liste mit Einladungslinks dazu findest du ebenfalls in der Gruppenbeschreibung.<br /><br />Falls du irgendwelche Fragen hast, kannst
# du dich jederzeit gerne an mich wenden.<br /><br />Liebe Grüße<br /><br />Marvin Ruder<br /><br /><br />––––––––––––––––––––––––––––––––<br /><br />Liberale Gamer e.V.<br /><br />Marvin Ruder<br />Mitgliederbetreuung<br /><br />Tel.:&tab; 06224 9266995<br />Fax:&tab; 06224 9282579<br />Mobil:&tab;0176 57517450<br /><br /><a href="mailto:marvin.ruder@liberale-gamer.gg">marvin.ruder@liberale-gamer.gg</a><br /><a href="https://www.liberale-gamer.gg">www.liberale-gamer.gg</a><br />"""

#     send_email(sender, receiver, subject, text)
