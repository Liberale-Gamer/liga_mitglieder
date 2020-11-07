#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import Flask , request, render_template, session, flash, redirect, url_for, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_login import LoginManager , UserMixin, login_user, login_required, logout_user, current_user
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemySchema
import hashlib
import numpy as np
import mailer
import time
from datetime import datetime , timedelta
import json
import copy
import sqlconfig
import urllib
import sendmail, getmail
import re
import ast
import emails

app = Flask(__name__)

#MySQL Verbindung
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@localhost/{}'.format(sqlconfig.sql_config.user,sqlconfig.sql_config.pw,\
sqlconfig.sql_config.db)


db = SQLAlchemy(app)

ma = Marshmallow(app)

login_manager = LoginManager()
login_manager.init_app(app)

class new_user():
  def __init__(self, vorname, name, sex, strasse, hausnummer,\
  plz, ort, geburtsdatum, erstellungsdatum, mobil, email,\
  geburtsdatum_string, erstellungsdatum_string):
    self.vorname = vorname
    self.name = name
    self.sex = sex
    self.strasse = strasse
    self.hausnummer = hausnummer
    self.plz = plz
    self.ort = ort
    self.geburtsdatum = geburtsdatum
    self.erstellungsdatum = erstellungsdatum
    self.mobil = mobil
    self.email = email
    self.geburtsdatum_string = geburtsdatum_string
    self.erstellungsdatum_string = erstellungsdatum_string

class mitglieder(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    vorname = db.Column(db.String(30)) 
    name = db.Column(db.String(30))
    sex = db.Column(db.Integer)
    strasse = db.Column(db.String(30))  
    hausnummer = db.Column(db.String(10))
    plz = db.Column(db.String(30))  
    ort = db.Column(db.String(30)) 
    geburtsdatum = db.Column(db.Integer)
    erstellungsdatum = db.Column(db.Integer)  
    mobil = db.Column(db.String(30))
    email = db.Column(db.String(50))
    #Ab hier leere Inhalte
    #sonstiges = db.Column(db.String(30), default="NULL")
    passwort = db.Column(db.String(30), default="12345")
    forum_id = db.Column(db.String(30))
    forum_username = db.Column(db.String(30))
    forum_passwort = db.Column(db.String(30), default="12345")
    token = db.Column(db.Text, default="")
    tokenttl = db.Column(db.Integer, default=0)
    rechte = db.Column(db.Integer, default=0)
    
class mitgliederSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = mitglieder
        load_instance = True  

class abstimmung_intern(UserMixin, db.Model):
    id = db.Column(db.String(30), primary_key = True)
    titel = db.Column(db.String(250))
    text = db.Column(db.Text(4294000000))
    stimmen = db.Column(db.String(250), default="NULL")
    status = db.Column(db.Integer)
    
class abstimmung_internSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = abstimmung_intern
        load_instance = True  



# class vorstand(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(30), unique = True)
#     kuerzel = db.Column(db.String(2))
#     passwort = db.Column(db.String(50))
#     email = db.Column(db.String(50))
#     token = db.Column(db.String(50))
#     tokenttl = db.Column(db.Integer)
#     rechte = db.Column(db.Integer)
    
#Redirect if trying to access protected page
login_manager.login_view = "login" 
#Secret session key (TODO: RANDOMIZE)
ran = np.random.randint(9999999999) * np.random.randint(9999999999)
app.secret_key = hashlib.sha3_256(str(ran).encode('utf-8')).hexdigest()

@login_manager.user_loader
def load_user(user_id):
    return mitglieder.query.get(int(user_id))  
    
@app.route('/')
def show_entries():
    return redirect(url_for('login'))

@app.route('/favicon.ico')
def favicon():
    return redirect('https://liberale-gamer.gg/favicon.ico')

@app.route('/index.html')
def index():
    return redirect(url_for('login'))   
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if current_user.is_authenticated == True:
        return redirect(url_for('home'))
    else:
        pass    
    if request.method == 'POST':
        user = mitglieder.query.filter_by(email=request.form['username']).first()
        if user == None:
            error = 'Dieser Benutzer existiert nicht'
            return render_template('login.html',error=error)
        password = hashlib.sha3_256(str(request.form['password']).encode('utf-8')).hexdigest()
        if password == user.passwort:
            login_user(user,remember=True,duration=timedelta(300))
            if request.args.get('next') != '' and request.args.get('next') != None:
                return redirect(request.args.get('next'))
            return redirect(url_for('home'))
        else:
            error = 'Das Passwort ist falsch'
    else:
        password = None
        pass
    if request.args.get('next') != '' and request.args.get('next') != None:
        return render_template('login.html',error=error,next=request.args.get('next'),null=request.args.get('null'))
    return render_template('login.html',error=error)

    
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    geburtsdatum = format(datetime.fromtimestamp(current_user.geburtsdatum+7200), '%d.%m.%Y')
    erstellungsdatum = format(datetime.fromtimestamp(current_user.erstellungsdatum), '%d.%m.%Y')
    if request.method == 'POST':
        if "change_password" in request.form:
            password = hashlib.sha3_256(str(request.form['old_password']).encode('utf-8')).hexdigest()
            if password == current_user.passwort and request.form['new_password'] == request.form['confirm_password'] and request.form['new_password'] != '':
                flash('Passwort aktualisiert')
                new_pw = hashlib.sha3_256(str(request.form['new_password']).encode('utf-8')).hexdigest()
                current_user.passwort = new_pw
                db.session.commit()
                return render_template('home.html', geburtsdatum=geburtsdatum, erstellungsdatum=erstellungsdatum) 
            else:
                if password != current_user.passwort:
                    flash('Altes Passwort falsch')
                if request.form['new_password'] != request.form['confirm_password']:
                    flash('Passwörter stimmen nicht überein')
                if request.form['new_password'] == '':
                    flash('Bitte gib ein neues Passwort ein')
        if "change_data" in request.form:
            if request.form['strasse'] != '':
                current_user.strasse = request.form['strasse']
            if request.form['hausnummer'] != '':
                current_user.hausnummer = request.form['hausnummer']
            if request.form['plz'] != '':
                current_user.plz = request.form['plz']
            if request.form['ort'] != '':
                current_user.ort = request.form['ort']
            if request.form['email'] != '':
                current_user.email = request.form['email']
            if request.form['mobil'] != '':
                current_user.mobil = request.form['mobil']
            db.session.commit()
            flash('Daten aktualisiert')
            return render_template('home.html', geburtsdatum=geburtsdatum, erstellungsdatum=erstellungsdatum)
    else:
        pass
    return render_template('home.html', geburtsdatum=geburtsdatum, erstellungsdatum=erstellungsdatum)

#Routine for forgotten password
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        email = request.form['email']
        token = hashlib.sha3_256(str(np.random.randint(999999999999999)).encode('utf-8')).hexdigest()
        token2 = hashlib.sha3_256(str(np.random.randint(999999999999999)).encode('utf-8')).hexdigest()
        
        user = mitglieder.query.filter_by(email=request.form['email']).first()
        user.token = token + token2
        user.tokenttl = int(time.time()) + 300
        db.session.commit()
        
        sender = "LiGa-Mitgliederdatenbank <reset@liberale-gamer.gg>"

        tokenttl = format(datetime.fromtimestamp(user.tokenttl), '%d.%m.%Y um %H:%M Uhr')

        text = """\
Hallo {},

Der Link zum Zurücksetzen deines Passworts lautet: 
{}

Der Link ist gültig bis zum {}.""".format(user.vorname,"https://mitgliederverwaltung.liberale-gamer.gg/reset/"+user.token, tokenttl) 
        mailer.send_email(sender, email, "Passwort zurücksetzen", text)
        flash('E-Mail wurde gesendet an {}'.format(email))
    return render_template('reset.html')
    
#Actually reset the password
@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_pw(token):
    user = mitglieder.query.filter_by(token=token).first()
    if user.tokenttl < int(time.time()):
        flash('Dein Token ist abgelaufen')
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            if request.form['new_password'] == request.form['confirm_password'] and request.form['new_password'] != '':
                user.passwort = hashlib.sha3_256(str(request.form['new_password']).encode('utf-8')).hexdigest()
                db.session.commit()
                flash('Passwort zurückgesetzt')
                return render_template('login.html')
            else:
                if request.form['new_password'] != request.form['confirm_password']:
                    flash('Passwörter stimmen nicht überein')
                if request.form['new_password'] == '':
                    flash('Bitte gib ein neues Passwort ein')            
    return render_template('reset_pw.html',token=token)


   
@app.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if current_user.rechte < 2:
        flash('Keine Berechtigung')
        return redirect(url_for('home'))
    antrags_id = request.args.get('antrags_id')
    subjects=getmail.get_subjects()
    subjects.reverse()
    ids = []
    for subject in subjects:
        ids.append(re.findall('\d+', subject)[0])
    ids_subjects = zip(ids, subjects)
    if request.method == 'GET':
        if antrags_id != None:
            return render_template('new.html', ids_subjects=ids_subjects, imap_antrag=getmail.get_mail(antrags_id), antrags_id=antrags_id)
        return render_template('new.html', ids_subjects=ids_subjects)
    if request.method == 'POST':
        if request.form["antrags_id"].isnumeric():
            return render_template('new.html', ids_subjects=ids_subjects, imap_antrag=getmail.get_mail(request.form["antrags_id"]), antrags_id=request.form["antrags_id"])
        else:
            return render_template('new.html', ids_subjects=ids_subjects)

    
@app.route('/database')
@login_required
def database():
    if current_user.rechte < 2:
        flash('Keine Berechtigung')
        return redirect(url_for('home'))
    all_users = mitglieder.query.order_by(-mitglieder.id)
    mitgliederschema = mitgliederSchema(many=True)
    output = mitgliederschema.dumps(all_users)
    data_json = jsonify({'name' : output})
    return render_template('database.html',output = output)
    #return output


@app.route('/abstimmung', methods=['GET', 'POST'])
@login_required
def abstimmung_list():
    if current_user.rechte < 1:
        flash('Keine Berechtigung')
        return redirect(url_for('home'))
    subjects=getmail.get_subjects()
    subjects.reverse()
    ids = []
    for subject in subjects:
        ids.append(re.findall('\d+', subject)[0])
    ids_subjects = zip(ids, subjects)
    all_abstimmungen = abstimmung_intern.query
    abstimmungschema = abstimmung_internSchema(many=True)
    output = abstimmungschema.dumps(all_abstimmungen)
    abstimmungen = ast.literal_eval(output)
    if request.method == 'GET':
        return render_template('abstimmung_list.html', abstimmungen=abstimmungen, ids_subjects=ids_subjects, imap_antrag=None, name="")
    if request.method == 'POST':
        if 'antrags_id' in request.form:
            if request.form["antrags_id"].isnumeric():
                name=""
                for subject in subjects:
                    if subject.find(request.form["antrags_id"]) != -1:
                        name=subject[subject.find("] ") + 2:]
                return render_template('abstimmung_list.html', abstimmungen=abstimmungen, ids_subjects=ids_subjects, imap_antrag=getmail.get_mail(request.form["antrags_id"], redact = True), antrags_id=request.form["antrags_id"], name=name)
            else:
                return render_template('abstimmung_list.html', abstimmungen=abstimmungen, ids_subjects=ids_subjects, imap_antrag=None, name="")
        antrag_add = abstimmung_intern()
        if request.form['titel'][0:request.form['titel'].find(' ')].isnumeric():
            antrag_add.id = request.form['titel'][0:request.form['titel'].find(' ')]
            antrag_add.titel = request.form['titel'][request.form['titel'].find(' ') + 1:]
        else:
            antrag_add.id = datetime.now().strftime("%Y%m%d%H%M%S")
            antrag_add.titel = request.form['titel']
        antrag_add.text = "Der Vorstand wolle beschließen:\n\n" + request.form['text']
        antrag_add.stimmen = "{}"
        antrag_add.status = 1
        db.session.add(antrag_add)
        db.session.commit()
        subject = f"Neuer Antrag: {antrag_add.titel}"
        antrag_add.text = antrag_add.text.replace('\n', '<br>')
        text = f"""
Der nachfolgende Antrag wurde gestellt:<br />
<br />
<strong>{antrag_add.titel}</strong><br />
<br />
{antrag_add.text}<br />
<br />
<a href="https://mitgliederverwaltung.liberale-gamer.gg/abstimmung/{antrag_add.id}">Jetzt abstimmen</a>"""
        if request.host.find("localhost") != -1:
            emails.vorstand = emails.developer
            print("Development mode, sending motion mails to " + emails.vorstand)
        sendmail.send_email(sender='Dein freundliches LiGa-Benachrichtigungssystem <mitgliedsantrag@liberale-gamer.gg>',\
        receiver=emails.vorstand, subject=subject, text=text)
        return redirect(url_for('abstimmung_list'))
    
@app.route('/abstimmung/<abstimmung_id>', methods=['GET', 'POST'])
@login_required
def abstimmung(abstimmung_id):
    if current_user.rechte < 1:
        flash('Keine Berechtigung')
        return redirect(url_for('home'))
    all_abstimmungen = abstimmung_intern.query
    abstimmungschema = abstimmung_internSchema(many=True)
    output = abstimmungschema.dumps(all_abstimmungen)
    abstimmungen = ast.literal_eval(output)
    for abstimmung in abstimmungen:
        if abstimmung.get('id') == abstimmung_id:
            abstimmung['stimmen'] = ast.literal_eval(abstimmung.get('stimmen'))
            if request.method == 'GET':
                engine = create_engine('mysql+pymysql://{}:{}@localhost/{}'.format(sqlconfig.sql_config.user,sqlconfig.sql_config.pw,sqlconfig.sql_config.db))
                with engine.connect() as con:
                    abstimmungsberechtigte_count = con.execute("SELECT count(id) FROM mitglieder WHERE rechte > 0").fetchone()[0]
                alle_da = False
                if abstimmungsberechtigte_count == len(abstimmung['stimmen']):
                    alle_da = True
                zust = sum(1 for value in abstimmung.get('stimmen').values() if value == 'Zustimmung')
                enth = sum(1 for value in abstimmung.get('stimmen').values() if value == 'Enthaltung')
                abl = sum(1 for value in abstimmung.get('stimmen').values() if value == 'Ablehnung')
                abstimmung['text'] = abstimmung['text'].replace('\n', '<br>')
                return render_template('abstimmung.html', abstimmung=abstimmung, alle_da=alle_da, zust=zust, enth=enth, abl=abl)
            if request.method == 'POST':
                if 'reopen' in request.form:
                    abstimmung_changes = abstimmung_intern.query.filter_by(id=abstimmung_id).first()
                    abstimmung_changes.status = 1
                    db.session.commit()
                    flash('Abstimmung fortgesetzt')
                    return redirect(url_for('abstimmung_list'))

                elif 'end' in request.form:
                    if request.form['action'] == 'delete':
                        antrag = abstimmung_intern.query.filter_by(id=abstimmung_id).first()
                        db.session.delete(antrag)
                        db.session.commit()
                        flash('Antrag gelöscht')
                    else:
                        subject = f"Antrag {request.form['action']}: {abstimmung['titel']}"
                        abstimmung['text'] = abstimmung['text'].replace('\n', '<br>')
                        abstimmung['stimmen'] = str(abstimmung['stimmen'])\
                        .replace(',', '<br>').replace('{', '').replace('}', '')
                        text = f"""
Der nachfolgende Antrag wurde {request.form['action']}:<br />
<br />
<strong>{abstimmung['titel']}</strong><br />
<br />
{abstimmung['text']}<br />
<br />
Abgegebene Stimmen:<br />
{str(abstimmung['stimmen'])}"""
                        if request.host.find("localhost") != -1:
                            emails.vorstand = emails.developer
                            print("Development mode, sending motion mails to " + emails.vorstand)
                        sendmail.send_email(sender='Dein freundliches LiGa-Benachrichtigungssystem <mitgliedsantrag@liberale-gamer.gg>',\
                        receiver=emails.vorstand, subject=subject, text=text)
                        abstimmung_changes = abstimmung_intern.query.filter_by(id=abstimmung_id).first()
                        abstimmung_changes.status = 0
                        db.session.commit()
                        flash('Antrag ' + request.form['action'])
                        if len(str(abstimmung['id'])) <= 6 and request.form['action'] == 'angenommen':
                            return redirect(url_for('new', antrags_id=abstimmung_id))
                    return redirect(url_for('abstimmung_list'))

                if request.form['votum'] == 'clear':
                    if current_user.vorname + ' ' + current_user.name in abstimmung['stimmen']:
                        abstimmung['stimmen'].pop(current_user.vorname + ' ' + current_user.name)
                        flash('Dein Votum wurde zurückgesetzt')
                else:
                    abstimmung['stimmen'][current_user.vorname + ' ' + current_user.name] = request.form['votum']
                    flash('Dein Votum wurde erfasst')
                    engine = create_engine('mysql+pymysql://{}:{}@localhost/{}'.format(sqlconfig.sql_config.user,sqlconfig.sql_config.pw,sqlconfig.sql_config.db))
                    with engine.connect() as con:
                        abstimmungsberechtigte_count = con.execute("SELECT count(id) FROM mitglieder WHERE rechte > 0").fetchone()[0]
                    alle_da = False
                    if abstimmungsberechtigte_count == len(abstimmung['stimmen']):
                        alle_da = True
                    if alle_da:
                        if len(str(abstimmung['id'])) <= 6:
                            receiver = emails.mitgliederbetreuung
                        else:
                            receiver = emails.vorsitz
                        subject = f"Alle Stimmen abgegeben: {abstimmung['titel']}"
                        text = f"""
Zum Antrag „<strong>{abstimmung['titel']}</strong>“ haben alle Berechtigten abgestimmt.<br />
<br />
<a href="https://mitgliederverwaltung.liberale-gamer.gg/abstimmung/{abstimmung['id']}">Jetzt Abstimmung beenden</a>"""
                        sendmail.send_email(sender='Dein freundliches LiGa-Benachrichtigungssystem <mitgliedsantrag@liberale-gamer.gg>',\
                        receiver=receiver, subject=subject, text=text)                        
                abstimmung_changes = abstimmung_intern.query.filter_by(id=abstimmung_id).first()
                abstimmung_changes.stimmen = str(abstimmung['stimmen'])
                db.session.commit()
                return redirect(url_for('abstimmung', abstimmung_id=abstimmung_id))
    flash('Abstimmung nicht gefunden')
    return redirect(url_for('abstimmung_list'))
    
@app.route('/edit/<user_id>')
@login_required
def edit(user_id):
    if current_user.rechte < 2:
        flash('Keine Berechtigung')
        return redirect(url_for('home'))

    user = mitglieder.query.filter_by(id=user_id).first()
    

    geburtsdatum = format(datetime.fromtimestamp(user.geburtsdatum+7200), '%d.%m.%Y')
    erstellungsdatum = format(datetime.fromtimestamp(user.erstellungsdatum), '%d.%m.%Y')
    

    session['user_id'] = user_id
        
    return render_template('edit.html',user = user, geburtsdatum=geburtsdatum,\
    erstellungsdatum=erstellungsdatum)
    
@app.route('/send_mail/<user_id>', methods=['GET', 'POST'])
@login_required
def send_mail(user_id):
    if current_user.rechte < 2:
        flash('Keine Berechtigung')
        return redirect(url_for('home'))

    user = mitglieder.query.filter_by(id=user_id).first()
        
    geburtsdatum = format(datetime.fromtimestamp(user.geburtsdatum+7200), '%d.%m.%Y')
    erstellungsdatum = format(datetime.fromtimestamp(user.erstellungsdatum), '%d.%m.%Y')
        
    session['user_id'] = user_id

    url_vorname = urllib.parse.quote_plus(user.vorname)
    url_name = urllib.parse.quote_plus(user.name)
    
    receiver = f"{user.vorname} {user.name} <{user.email}>"
    subject = f"Herzlich willkommen bei den Liberalen Gamern, {user.vorname}!"

    text = f"""\
Hallo {user.vorname},<br />
<br />
ich bin Marvin von den Liberalen Gamern und möchte dich bei uns herzlich willkommen heißen!<br />
<br />
Wir haben dich mit den folgenden Daten in unser Mitgliederverzeichnis aufgenommen &ndash; schau einmal, ob alles richtig ist:<br />
<br />
Vorname: {user.vorname}<br />
Name: {user.name}<br />
Anschrift: {user.strasse}&nbsp;{user.hausnummer}<br />
PLZ, Ort: {user.plz}&nbsp;{user.ort}<br />
E-Mail-Adresse: {user.email}<br />
Handynummer: {user.mobil}<br />
Geburtsdatum: {geburtsdatum}<br />
<br />
Mitgliedsnummer: {user_id}<br />
<br />
Hier noch ein paar hilfreiche Links rund um die LiGa:<br />
<br />
Unsere offiziellen Social-Media-Kanäle (gerne teilen und liken):<br />
<a href="https://www.facebook.com/liberalegamer">https://www.facebook.com/liberalegamer</a><br />
<a href="https://twitter.com/LiberaleGamer">https://twitter.com/LiberaleGamer</a><br />
<a href="https://www.instagram.com/LiberaleGamer">https://www.instagram.com/LiberaleGamer</a><br />
<br />
Unsere verbandsinternen Dokumente wie Beschlüsse, Satzung oder Geschäftsordnung dokumentieren wir in unserem Wiki: <a href="https://wiki.liberale-gamer.gg">https://wiki.liberale-gamer.gg</a><br />
<br />
Unsere geschlossene Facebook-Gruppe: <a href="https://www.facebook.com/groups/433296140360035/">https://www.facebook.com/groups/433296140360035/</a><br />
Unserer geschlossenen WhatsApp-Gruppe kann ich dich hinzufügen, wenn du mir dafür auf WhatsApp eine kurze Nachricht schreibst &ndash; mit <a href="https://api.whatsapp.com/send?phone=4917657517450&text=Hallo+Marvin%2C+bitte+f%C3%BCge+mich+der+LiGa-WhatsApp-Gruppe+hinzu%21+{url_vorname}+{url_name}+%28Mitgliedsnummer+{user_id}%29%2E%20Ich+bin+damit+einverstanden%2C+dass+mit+Hinzuf%C3%BCgen+in+diese+Gruppe+meine+Handynummer+an+WhatsApp+und+alle+Mitglieder+in+der+Gruppe+weitergegeben+wird%2E">diesem Link</a> geht das ganz einfach. Dazu ein notwendiger Hinweis zum Datenschutz: Wenn du uns mitteilst, dass du zu unserer LiGa-WhatsApp-Gruppe hinzugefügt werden möchtest, erklärst du dich damit einverstanden, dass mit Hinzufügen in diese Gruppe deine Handynummer an WhatsApp und alle Mitglieder in der Gruppe weitergegeben wird.<br />
<br />
Noch ein kurzer Hinweis zu der WhatsApp-Gruppe: Diese ist ausschließlich für Vereins- und Gaming-Themen gedacht. Du findest in der Gruppenbeschreibung aber auch einen Link zur LiGa-Talk-Gruppe, in der über alles Mögliche diskutiert werden kann. Auch haben wir weitere Gruppen speziell für einzelne Spiele eingerichtet. Eine Liste mit Einladungslinks dazu findest du ebenfalls in der Gruppenbeschreibung.<br />
<br />
Falls du irgendwelche Fragen hast, kannst du dich jederzeit gerne an mich wenden.<br />
<br />
Liebe Grüße<br />
<br />
Marvin Ruder<br />
<br />
<br />
————————————————————————————————<br />
<br />
Liberale Gamer e.V.<br />
<br />
Marvin Ruder<br />
Mitgliederbetreuung<br />
<br />
Tel.:   06224 9266995<br />
Fax:    06224 9282579<br />
Mobil:  0176 57517450<br />
<br />
<a href="mailto:marvin.ruder@liberale-gamer.gg">marvin.ruder@liberale-gamer.gg</a><br />
<a href="https://www.liberale-gamer.gg">www.liberale-gamer.gg</a><br />"""

    url_receiver = urllib.parse.quote_plus(receiver)
    url_subject = urllib.parse.quote_plus(subject)
    url_text = urllib.parse.quote_plus(text)
    link = f"mailto:{url_receiver}?subject={url_subject}&body={url_text}"
    if request.method == 'GET':
        return render_template('send_mail.html',user = user, geburtsdatum=geburtsdatum,\
        erstellungsdatum=erstellungsdatum, text=text, subject=subject, link=link)
    
    if request.method == 'POST':
        if "send" in request.form:
            sendmail.send_email(emails.mitgliederbetreuung_mitgliedsantrag, receiver, subject, text, emails.mitgliederbetreuung)
            flash('Mail versendet')
            return redirect(url_for('edit',user_id=str(user_id)))
        return redirect(url_for('edit',user_id=str(user_id)))


@app.route('/confirm_edit',methods=['GET','POST'])
@login_required
def confirm_edit():
    if current_user.rechte < 2:
        flash('Keine Berechtigung')
        return redirect(url_for('home'))
    if request.method == 'POST':
        user = mitglieder.query.filter_by(id=session["user_id"]).first()
        geburtsdatum = format(datetime.fromtimestamp(user.geburtsdatum+7200), '%d.%m.%Y')
        erstellungsdatum = format(datetime.fromtimestamp(user.erstellungsdatum), '%d.%m.%Y')
        if "delete" in request.form:
            return render_template('confirm_edit.html', user=user,delete=1, geburtsdatum=geburtsdatum,\
    erstellungsdatum=erstellungsdatum)
        if "confirm_delete" in request.form:
            db.session.delete(user)
            db.session.commit()
            flash('Mitglied gelöscht')
            return render_template('confirm_edit.html', confirm_delete=1, user=user)
        if "aktualisieren" in request.form:
            user_old = copy.copy(user)
            for item in user.__dict__:      
                try:
                    if request.form[item] == "":
                        continue
                    if request.form[item] == "-":
                        vars(user)[item] = ""
                    elif vars(user)[item] != request.form[item]:
                        vars(user)[item] = request.form[item]
                except:
                    pass        
            return render_template('confirm_edit.html', edit=1, user_old=user_old,user=user, geburtsdatum=geburtsdatum,\
    erstellungsdatum=erstellungsdatum)            
        if "confirm_edit" in request.form:
            user.name = request.form["name"]
            user.vorname = request.form["vorname"]
            user.strasse = request.form["strasse"]
            user.hausnummer = request.form["hausnummer"]
            user.plz = request.form["plz"]
            user.ort = request.form["ort"]
            user.email = request.form["email"]
            user.mobil = request.form["mobil"]
            user.rechte = request.form["rechte"]
        
            db.session.commit()
        
            flash('Änderungen übernommen')
            return redirect(url_for('edit',user_id=str(user.id)))
    return render_template('confirm_edit.html')
    
@app.route('/confirm_new',methods=['GET','POST'])
@login_required
def confirm_new():
    if current_user.rechte < 2:
        flash('Keine Berechtigung')
        return redirect(url_for('home'))
    if "new" in request.form and request.method == 'POST':
        geburtsdatum = int(time.mktime(datetime.strptime(request.form["geburtsdatum"], "%Y-%m-%d").timetuple()))+7200
        geburtsdatum_string = format(datetime.fromtimestamp(geburtsdatum), '%d.%m.%Y')
        erstellungsdatum_string = format(datetime.fromtimestamp(int(time.time())), '%d.%m.%Y')
        new = new_user(request.form["vorname"],request.form["name"], request.form["sex"],\
        request.form["strasse"], request.form["hausnummer"],request.form["plz"],\
        request.form["ort"], geburtsdatum,int(time.time()),\
        request.form["mobil"], request.form["email"], geburtsdatum_string, erstellungsdatum_string)
        return render_template('confirm_new.html', confirm=1, new=new)
    if "confirm_new" in request.form and request.method == 'POST':
        
        user_add = mitglieder()
        user_add.name = request.form["name"]
        user_add.vorname = request.form["vorname"]
        user_add.sex = request.form["sex"]
        user_add.strasse = request.form["strasse"]
        user_add.hausnummer = request.form["hausnummer"]
        user_add.plz = request.form["plz"]
        user_add.ort = request.form["ort"]
        user_add.geburtsdatum = request.form["geburtsdatum"]
        user_add.erstellungsdatum = request.form["erstellungsdatum"]
        user_add.mobil = request.form["mobil"]
        user_add.email = request.form["email"]
        user_add.forum_id = 1
        user_add.forum_username = request.form["vorname"]
        
        db.session.add(user_add)
        db.session.commit()
        
        newest_id = mitglieder.query.order_by(-mitglieder.id).first()
        
        return render_template('confirm_new.html', created=1, newest_id=newest_id)
    
    return render_template('confirm_new.html')

@app.route('/set_counter', methods=['GET','POST'])
@login_required
def set_counter():
    if current_user.rechte < 2:
        flash('Keine Berechtigung')
        return redirect(url_for('home'))
    engine = create_engine('mysql+pymysql://{}:{}@localhost/{}'.format(sqlconfig.sql_config.user,sqlconfig.sql_config.pw,sqlconfig.sql_config.db))
    with engine.connect() as con:
        old_counter = con.execute("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'liga_intern_de' AND TABLE_NAME = 'mitglieder'")
        newest_member = con.execute("SELECT id FROM mitglieder WHERE id = (SELECT max(id) FROM mitglieder);")
    if request.method == 'GET':
        return render_template('set_counter.html', old_counter=old_counter.fetchone()[0],newest_member=newest_member.fetchone()[0])
    if request.method == 'POST':
        if request.form["new_counter"].isnumeric():
            with engine.connect() as con:
                con.execute("ALTER TABLE mitglieder AUTO_INCREMENT = " + request.form["new_counter"])
                old_counter = con.execute("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'liga_intern_de' AND TABLE_NAME = 'mitglieder'")
                newest_member = con.execute("SELECT id FROM mitglieder WHERE id = (SELECT max(id) FROM mitglieder);")
        else:
            flash("Bitte gib eine Zahl ein")
        return render_template('set_counter.html', old_counter=old_counter.fetchone()[0],newest_member=newest_member.fetchone()[0])
            

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Du wurdest ausgeloggt')
    return redirect(url_for('login'))
