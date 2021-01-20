#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, session, flash, redirect, url_for, g, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_login import LoginManager , UserMixin, login_user, login_required, logout_user, current_user
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemySchema
import hashlib
import numpy as np
import time
from datetime import datetime, timedelta
import json
import copy
import sqlconfig
import urllib
import sendmail, getmail
import re
import ast
import emails
import files
import get_key
import crypto
import os
import sys
import grouplinks
import util
from context import webauthn

app = Flask(__name__)

#MySQL Verbindung
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@localhost/{}'.format(sqlconfig.sql_config.user,sqlconfig.sql_config.pw,\
sqlconfig.sql_config.db)


db = SQLAlchemy(app)

sk = os.environ.get('FLASK_SECRET_KEY')

ma = Marshmallow(app)
app.secret_key = sk if sk else os.urandom(40)

login_manager = LoginManager()
login_manager.init_app(app)

RP_ID = 'liberale-gamer.gg'
RP_NAME = 'LiGa-Mitgliedersystem'
ORIGIN = 'https://intern.liberale-gamer.gg'

# Trust anchors (trusted attestation roots) should be
# placed in TRUST_ANCHOR_DIR.
TRUST_ANCHOR_DIR = 'trusted_attestation_roots'


# After how many seconds of inactivity a user is logged out
session_ttl = 5 # e.g. 5 minutes

#Before each request, check if session is alive.
#If it is, reset the inacitivity timer
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=session_ttl)
    session.modified = True

class new_user():
    def __init__(self, vorname, name, sex, strasse, hausnummer,\
plz, ort, geburtsdatum, erstellungsdatum, mobil, email,\
sonstiges, geburtsdatum_string, erstellungsdatum_string, payed_till):
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
        self.sonstiges = sonstiges
        self.payed_till = payed_till


class mitglieder_no_sonstiges(UserMixin, db.Model):
    __tablename__ = 'mitglieder'
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
    #sonstiges = db.Column(db.Text(4294000000), default="")
    passwort = db.Column(db.String(30), default="")
    forum_id = db.Column(db.String(30))
    forum_username = db.Column(db.String(30))
    forum_passwort = db.Column(db.String(30), default="")
    token = db.Column(db.Text, default="")
    tokenttl = db.Column(db.Integer, default=0)
    rechte = db.Column(db.Integer, default=0)
    schluessel = db.Column(db.String(250))
    payed_till = db.Column(db.Integer, default=2018)
    ukey = db.Column(db.String(20), nullable=False)
    credential_id = db.Column(db.String(250), nullable=False)
    pub_key = db.Column(db.String(65), nullable=True)

class mitgliederNoSonstigesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = mitglieder_no_sonstiges
        load_instance = True

class mitglieder(UserMixin, db.Model):
    __tablename__ = 'mitglieder'
    __table_args__ = {'extend_existing': True}
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
    sonstiges = db.Column(db.Text(4294000000), default="")
    passwort = db.Column(db.String(30), default="")
    forum_id = db.Column(db.String(30))
    forum_username = db.Column(db.String(30))
    forum_passwort = db.Column(db.String(30), default="")
    token = db.Column(db.Text, default="")
    tokenttl = db.Column(db.Integer, default=0)
    rechte = db.Column(db.Integer, default=0)
    schluessel = db.Column(db.String(250))
    payed_till = db.Column(db.Integer, default=2018)
    ukey = db.Column(db.String(20), nullable=False)
    credential_id = db.Column(db.String(250), nullable=False)
    pub_key = db.Column(db.String(65), nullable=True)

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
    mitgliedsnummer = request.cookies.get('id')
    error = None
    if current_user.is_authenticated == True:
        if request.args.get('next') != '' and request.args.get('next') != None:
            response = make_response(redirect(request.args.get('next')))
        else:
            response = make_response(redirect(url_for('home')))
        if current_user.ukey != None or current_user.ukey != "":
            response.set_cookie('id', str(current_user.id).encode('utf-8'), max_age=60*60*24*365*2)
        return response
    if request.method == 'POST':
        user = mitglieder.query.filter_by(email=request.form['username']).first()
        if user == None:
            error = 'Dieser Benutzer existiert nicht'
            return render_template('login.html',error=error,mitgliedsnummer=mitgliedsnummer)
        password = hashlib.sha3_256(str(request.form['password']).encode('utf-8')).hexdigest()
        if password == user.passwort:
            login_user(user,remember=False,duration=timedelta(minutes=session_ttl))
            if request.args.get('next') != '' and request.args.get('next') != None:
                response = make_response(redirect(request.args.get('next')))
            else:
                response = make_response(redirect(url_for('home')))
            if current_user.ukey != None or current_user.ukey != "":
                response.set_cookie('id', str(current_user.id).encode('utf-8'), max_age=60*60*24*365*2)
            return response
        else:
            error = 'Das Passwort ist falsch'
    else:
        password = None
        pass
    if request.args.get('next') != '' and request.args.get('next') != None:
        return render_template('login.html',error=error,mitgliedsnummer=mitgliedsnummer,next=request.args.get('next'),null=request.args.get('null'))
    return render_template('login.html',error=error,mitgliedsnummer=mitgliedsnummer)

@app.route('/webauthn_begin_activate', methods=['POST'])
def webauthn_begin_activate():
    #clear session variables prior to starting a new registration
    session.pop('register_ukey', None)
    session.pop('register_id', None)
    session.pop('challenge', None)

    session['register_username'] = current_user.id
    session['register_display_name'] = current_user.vorname + " " + current_user.name

    challenge = util.generate_challenge(32)
    ukey = util.generate_ukey()

    # We strip the saved challenge of padding, so that we can do a byte
    # comparison on the URL-safe-without-padding challenge we get back
    # from the browser.
    # We will still pass the padded version down to the browser so that the JS
    # can decode the challenge into binary without too much trouble.
    session['challenge'] = challenge.rstrip('=')
    session['register_ukey'] = ukey

    make_credential_options = webauthn.WebAuthnMakeCredentialOptions(
        challenge, RP_NAME, RP_ID, ukey, current_user.id, current_user.vorname + " " + current_user.name,
        ORIGIN)

    return jsonify(make_credential_options.registration_dict)

@app.route('/webauthn_begin_assertion', methods=['POST'])
def webauthn_begin_assertion():
    username = request.form.get('login_username')

    user = mitglieder.query.filter_by(id=username).first()

    if not user:
        return make_response(jsonify({'fail': 'User does not exist.'}), 401)
    if not user.credential_id:
        return make_response(jsonify({'fail': 'Unknown credential ID.'}), 401)

    session.pop('challenge', None)

    challenge = util.generate_challenge(32)

    # We strip the padding from the challenge stored in the session
    # for the reasons outlined in the comment in webauthn_begin_activate.
    session['challenge'] = challenge.rstrip('=')

    webauthn_user = webauthn.WebAuthnUser(
        user.ukey, user.id, user.vorname + " " + user.name, "",
        user.credential_id, user.pub_key, 0, RP_ID)

    webauthn_assertion_options = webauthn.WebAuthnAssertionOptions(
        webauthn_user, challenge)

    return jsonify(webauthn_assertion_options.assertion_dict)

@app.route('/verify_credential_info', methods=['POST'])
def verify_credential_info():
    challenge = session['challenge']
    username = session['register_username']
    display_name = session['register_display_name']
    ukey = session['register_ukey']

    registration_response = request.form
    trust_anchor_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), TRUST_ANCHOR_DIR)
    trusted_attestation_cert_required = True
    self_attestation_permitted = True
    none_attestation_permitted = True

    webauthn_registration_response = webauthn.WebAuthnRegistrationResponse(
        RP_ID,
        ORIGIN,
        registration_response,
        challenge,
        trust_anchor_dir,
        trusted_attestation_cert_required,
        self_attestation_permitted,
        none_attestation_permitted,
        uv_required=False)  # User Verification

    try:
        webauthn_credential = webauthn_registration_response.verify()
    except Exception as e:
        return jsonify({'fail': 'Registration failed. Error: {}'.format(e)})

    # Step 17.
    #
    # Check that the credentialId is not yet registered to any other user.
    # If registration is requested for a credential that is already registered
    # to a different user, the Relying Party SHOULD fail this registration
    # ceremony, or it MAY decide to accept the registration, e.g. while deleting
    # the older registration.
    credential_id_exists = mitglieder.query.filter_by(
        credential_id=webauthn_credential.credential_id).first()
    if credential_id_exists:
        return make_response(
            jsonify({
                'fail': 'Credential ID already exists.'
            }), 401)

    if sys.version_info >= (3, 0):
        webauthn_credential.credential_id = str(
            webauthn_credential.credential_id, "utf-8")
        webauthn_credential.public_key = str(
            webauthn_credential.public_key, "utf-8")
    current_user.ukey = ukey
    current_user.pub_key=webauthn_credential.public_key
    current_user.credential_id=webauthn_credential.credential_id
    
    db.session.commit()

    flash('Erfolgreich registriert als {}.'.format(username))

    return jsonify({'success': 'User successfully registered.'})

@app.route('/verify_assertion', methods=['POST'])
def verify_assertion():
    challenge = session.get('challenge')
    assertion_response = request.form
    credential_id = assertion_response.get('id')

    user = mitglieder.query.filter_by(credential_id=credential_id).first()
    if not user:
        return make_response(jsonify({'fail': 'User does not exist.'}), 401)

    webauthn_user = webauthn.WebAuthnUser(
        user.ukey, user.id, user.vorname + " " + user.name, "",
        user.credential_id, user.pub_key, 0, RP_ID)

    webauthn_assertion_response = webauthn.WebAuthnAssertionResponse(
        webauthn_user,
        assertion_response,
        challenge,
        ORIGIN,
        uv_required=False)  # User Verification

    login_user(user,remember=False,duration=timedelta(minutes=session_ttl))

    return jsonify({
        'success':
        'Successfully authenticated as {}'.format(user.vorname + " " + user.name)
    })


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
                flash('Straße aktualisiert')
            if request.form['hausnummer'] != '':
                current_user.hausnummer = request.form['hausnummer']
                flash('Hausnummer aktualisiert')
            if request.form['plz'] != '':
                current_user.plz = request.form['plz']
                flash('PLZ aktualisiert')
            if request.form['ort'] != '':
                current_user.ort = request.form['ort']
                flash('Ort aktualisiert')
            if request.form['email'] != '':
                sender_name = "LiGa-Mitgliederdatenbank"
                text = """\
Hallo {},<br/>
<br/>
Der Link zum Aktualisieren deiner E-Mail-Adresse lautet: <br/>
{}""".format(current_user.vorname,"https://intern.liberale-gamer.gg/new_email/"+crypto.encrypt_message(request.form['email']).decode('utf-8')) 
                sendmail.send_email(sender_name, request.form['email'], "E-Mail-Adresse aktualisieren", text)
                flash('Eine E-Mail wurde gesendet an {}. Bitte klicke auf den Link darin, um deine E-Mail-Adresse zu aktualisieren.'.format(request.form['email']))
            if request.form['mobil'] != '':
                current_user.mobil = request.form['mobil']
                flash('Handynummer aktualisiert')
            db.session.commit()
            return render_template('home.html', geburtsdatum=geburtsdatum, erstellungsdatum=erstellungsdatum)
        if "newkey" in request.form:
            current_user.schluessel = get_key.get(current_user.schluessel)
            flash('Neuer Berechtigungsschlüssel generiert')
            db.session.commit()
            return render_template('home.html', geburtsdatum=geburtsdatum, erstellungsdatum=erstellungsdatum)
        if "removetoken" in request.form:
            current_user.ukey = ""
            current_user.credential_id = ""
            current_user.pub_key = ""
            flash('Sicherheitsschlüssel entfernt')
            db.session.commit()
            return render_template('home.html', geburtsdatum=geburtsdatum, erstellungsdatum=erstellungsdatum)
    else:
        pass
    return render_template('home.html', geburtsdatum=geburtsdatum, erstellungsdatum=erstellungsdatum)

@app.route('/send_member_email')
@login_required
def send_member_email():
    if current_user.rechte < 2:
        flash('Keine Berechtigung')
    else:
        engine = create_engine('mysql+pymysql://{}:{}@localhost/{}'.format(sqlconfig.sql_config.user,sqlconfig.sql_config.pw,sqlconfig.sql_config.db))
        with engine.connect() as con:
            email_result = con.execute("SELECT email FROM mitglieder")
        email_list = [[value for column, value in rowproxy.items()] for rowproxy in email_result]
        email_string = "mailto:info@liberale-gamer.gg?bcc="
        for email in email_list:
            email_string += email[0] + ','
        flash('<a href="' + email_string[:-1] + '" class="linkinflash">E-Mail senden</a>')
    return redirect(url_for('home'))

@app.route('/send_individual_email', methods=['GET', 'POST'])
@login_required
def send_individual_email():
    if current_user.rechte < 2:
        flash('Keine Berechtigung')
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('send_individual_email.html', hasbeentested=False)
    if request.method == 'POST':
        betreff=request.form['betreff']
        text=request.form['text']
        domain=request.form['domain']
        domain_whattodo=request.form['domain_whattodo']
        paid_filter=request.form["paid_filter"]
        receivers = []
        if paid_filter == "this_unpaid":
            paid_till = datetime.now().year
        elif paid_filter == "last_unpaid":
            paid_till = datetime.now().year - 1
        else:
            paid_till = 1e9
        if 'me' in request.form:
            receivers = [current_user]
        if 'board' in request.form:
            receivers = mitglieder.query.filter(mitglieder.rechte > 0).filter(mitglieder.payed_till < paid_till)
        if 'allmembers' in request.form:
            receivers = mitglieder.query.order_by(mitglieder.id).filter(mitglieder.payed_till < paid_till)
        if domain != "" and domain != None:
            if domain_whattodo == "include":
                receivers = receivers.filter(mitglieder.email.ilike("%" + domain))
            if domain_whattodo == "exclude":
                receivers = receivers.filter(mitglieder.email.notilike("%" + domain))
        if receivers != []:
            for receiver in receivers:
                anrede = ""
                geschlecht = ""
                if receiver.sex == 0:
                    anrede = "Herr"
                    geschlecht = "männlich"
                if receiver.sex == 1:
                    anrede = "Frau"
                    geschlecht = "weiblich"
                individual_betreff = betreff\
                    .replace("[id]", str(receiver.id))\
                    .replace("[vorname]", receiver.vorname)\
                    .replace("[name]", receiver.name)\
                    .replace("[anrede]", anrede)\
                    .replace("[geschlecht]", geschlecht)\
                    .replace("[strasse]", receiver.strasse)\
                    .replace("[hausnummer]", receiver.hausnummer)\
                    .replace("[plz]", receiver.plz)\
                    .replace("[ort]", receiver.ort)\
                    .replace("[geburtsdatum]", format(datetime.fromtimestamp(receiver.geburtsdatum+7200), '%d.%m.%Y'))\
                    .replace("[erstellungsdatum]", format(datetime.fromtimestamp(receiver.erstellungsdatum), '%d.%m.%Y'))\
                    .replace("[mobil]", receiver.mobil)\
                    .replace("[email]", receiver.email)\
                    .replace("[payed_till]", str(receiver.payed_till))
                individual_text = text\
                    .replace("\n", "<br />\n")\
                    .replace("[id]", str(receiver.id))\
                    .replace("[vorname]", receiver.vorname)\
                    .replace("[name]", receiver.name)\
                    .replace("[anrede]", anrede)\
                    .replace("[geschlecht]", geschlecht)\
                    .replace("[strasse]", receiver.strasse)\
                    .replace("[hausnummer]", receiver.hausnummer)\
                    .replace("[plz]", receiver.plz)\
                    .replace("[ort]", receiver.ort)\
                    .replace("[geburtsdatum]", format(datetime.fromtimestamp(receiver.geburtsdatum+7200), '%d.%m.%Y'))\
                    .replace("[erstellungsdatum]", format(datetime.fromtimestamp(receiver.erstellungsdatum), '%d.%m.%Y'))\
                    .replace("[mobil]", receiver.mobil)\
                    .replace("[email]", receiver.email)\
                    .replace("[payed_till]", str(receiver.payed_till))    
                sendmail.send_email('Liberale Gamer', 
                receiver.vorname + ' ' + receiver.name + '<' + receiver.email + '>', individual_betreff, individual_text, 
                replyto=current_user.vorname + ' ' + current_user.name + '<' + current_user.email + '>')
                flash("E-Mail gesendet an " + receiver.email)

        if 'me' in request.form or 'board' in request.form:
            return render_template('send_individual_email.html', hasbeentested=True, betreff=betreff, text=text, paid_filter=paid_filter, domain=domain, domain_whattodo=domain_whattodo)
        return render_template('send_individual_email.html', hasbeentested=False)



@app.route('/groups')
@login_required
def groups():
    return render_template('groups.html', main_groups=grouplinks.main_groups, gaming_groups=grouplinks.gaming_groups)


@app.route('/status')
@login_required
def status():
    status_map = {}
    for service_name in ['ts3', 'mc_server', 'sharelatex', 'ttt', 'jicofo', 'openslides']:
        status_code = os.system('service ' + service_name + ' status')
        if status_code != 0:
            status_map[service_name] = "<span style='color: #e5007d;'>offline #technikeristinformiert</span>"
            sender_name = "Dein freundliches LiGa-Benachrichtigungssystem"
            text = """Der Dienst „{}“ scheint offline zu sein.<br/>Mitglied Nr. {} hat dies entdeckt.""".format(service_name, current_user.id) 
            sendmail.send_email(sender_name, emails.it, "Dienst offline", text)
        else:
            status_map[service_name] = "<span style='color: #000000;'>online</span>"
    return render_template('status.html', status=status_map)


@app.route('/new_email/<token>')
@login_required
def new_email(token):
    new_email = crypto.decrypt_message(token.encode('utf-8')).decode('utf-8')
    current_user.email = new_email
    db.session.commit()
    flash('E-Mail-Adresse aktualisiert')
    return redirect(url_for('home'))

@app.route('/docs')
@login_required
def docs():
    return render_template('docs.html', filemap=files.filenames, foldermap=files.foldernames)

#Routine for forgotten password
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        email = request.form['email']
        token = hashlib.sha3_256(str(np.random.randint(999999999999999)).encode('utf-8')).hexdigest()
        token2 = hashlib.sha3_256(str(np.random.randint(999999999999999)).encode('utf-8')).hexdigest()
        
        user = mitglieder.query.filter_by(email=request.form['email']).first()
        if user == None:
            flash('Diese E-Mail-Adresse ist keinem Mitglied zugeordnet.')
            return render_template('reset.html')
        user.token = token + token2
        user.tokenttl = int(time.time()) + 900
        db.session.commit()
        
        sender_name = "LiGa-Mitgliederdatenbank"

        tokenttl = format(datetime.fromtimestamp(user.tokenttl), '%d.%m.%Y um %H:%M Uhr')

        text = """\
Hallo {},<br/>
<br/>
Der Link zum Zurücksetzen deines Passworts lautet: <br/>
{}<br/>
<br/>
Der Link ist gültig bis zum {}.""".format(user.vorname,"https://intern.liberale-gamer.gg/reset/"+user.token, tokenttl) 
        sendmail.send_email(sender_name, email, "Passwort zurücksetzen", text)
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
    if ids and subjects:
        ids_subjects = zip(ids, subjects)
    else:
        ids_subjects = None
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
    all_users = mitglieder_no_sonstiges.query.order_by(-mitglieder_no_sonstiges.id)
    mitgliederschema = mitgliederNoSonstigesSchema(many=True)
    output = mitgliederschema.dumps(all_users)
    data_json = jsonify({'name' : output})
    return render_template('database.html',output = output)


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
    if ids and subjects:
        ids_subjects = zip(ids, subjects)
    else:
        ids_subjects = None
    all_abstimmungen = abstimmung_intern.query
    abstimmungschema = abstimmung_internSchema(many=True)
    output = abstimmungschema.dumps(all_abstimmungen)
    abstimmungen = ast.literal_eval(output)
    zust = {}
    enth = {}
    abl = {}
    for abstimmung in abstimmungen:
        abstimmung['stimmen'] = ast.literal_eval(abstimmung.get('stimmen'))
        zust[abstimmung.get('id')] = sum(1 for value in abstimmung.get('stimmen').values() if value == 'Zustimmung')
        enth[abstimmung.get('id')] = sum(1 for value in abstimmung.get('stimmen').values() if value == 'Enthaltung')
        abl[abstimmung.get('id')] = sum(1 for value in abstimmung.get('stimmen').values() if value == 'Ablehnung')
    if request.method == 'GET':
        return render_template('abstimmung_list.html', abstimmungen=abstimmungen, zust=zust, enth=enth, abl=abl, ids_subjects=ids_subjects, imap_antrag=None, name="")
    if request.method == 'POST':
        if 'antrags_id' in request.form:
            if request.form["antrags_id"].isnumeric():
                name=""
                for subject in subjects:
                    if subject.find(request.form["antrags_id"]) != -1:
                        name=subject[subject.find("] ") + 2:]
                return render_template('abstimmung_list.html', abstimmungen=abstimmungen, zust=zust, enth=enth, abl=abl, ids_subjects=ids_subjects, imap_antrag=getmail.get_mail(request.form["antrags_id"], redact = True), antrags_id=request.form["antrags_id"], name=name)
            else:
                return render_template('abstimmung_list.html', abstimmungen=abstimmungen, zust=zust, enth=enth, abl=abl, ids_subjects=ids_subjects, imap_antrag=None, name="")
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
Der nachfolgende Antrag wurde gestellt:

<strong>{antrag_add.titel}</strong>

{antrag_add.text}

<a href="https://intern.liberale-gamer.gg/abstimmung/{antrag_add.id}">Jetzt abstimmen</a>"""
        if request.host.find("7997") == -1:
            emails.vorstand = emails.developer
            print("Development mode, sending motion mails to " + emails.vorstand)
        sendmail.send_email('Dein freundliches LiGa-Benachrichtigungssystem', emails.vorstand, subject, text.replace("\n", "<br />\n"))
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
                        abstimmung['stimmen'] = str(abstimmung['stimmen'])\
                        .replace(',', '\n').replace('{', '').replace('}', '')
                        text = f"""
Der nachfolgende Antrag wurde {request.form['action']}:

<strong>{abstimmung['titel']}</strong>

{abstimmung['text']}

Abgegebene Stimmen:
{str(abstimmung['stimmen'])}

Die Feststellung des Stimmergebnisses erfolgte durch {current_user.vorname} {current_user.name}."""
                        if request.host.find("7997") == -1:
                            emails.vorstand = emails.developer
                            print("Development mode, sending motion mails to " + emails.vorstand)
                        sendmail.send_email('Dein freundliches LiGa-Benachrichtigungssystem', emails.vorstand, subject, text.replace("\n", "<br />\n"))
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
<a href="https://intern.liberale-gamer.gg/abstimmung/{abstimmung['id']}">Jetzt Abstimmung beenden</a>"""
                        sendmail.send_email('Dein freundliches LiGa-Benachrichtigungssystem', receiver, subject, text)                        
                abstimmung_changes = abstimmung_intern.query.filter_by(id=abstimmung_id).first()
                abstimmung_changes.stimmen = str(abstimmung['stimmen'])
                db.session.commit()
                return redirect(url_for('abstimmung', abstimmung_id=abstimmung_id))
    flash('Abstimmung nicht gefunden')
    return redirect(url_for('abstimmung_list'))
    
@app.route('/edit/<user_id>', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    if current_user.rechte < 2:
        flash('Keine Berechtigung')
        return redirect(url_for('home'))

    if request.method == 'GET':
        user = mitglieder.query.filter_by(id=user_id).first()
        
        geburtsdatum = format(datetime.fromtimestamp(user.geburtsdatum+7200), '%d.%m.%Y')
        erstellungsdatum = format(datetime.fromtimestamp(user.erstellungsdatum), '%d.%m.%Y')
        
        session['user_id'] = user_id
            
        return render_template('edit.html', user = user, geburtsdatum=geburtsdatum,\
        erstellungsdatum=erstellungsdatum)
    if request.method == 'POST':
        user = mitglieder.query.filter_by(id=user_id).first()
        user.schluessel = get_key.get(user.schluessel)
        db.session.commit()
        return redirect(url_for('edit',user_id=str(user_id)))
    
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
ich bin {current_user.vorname} von den Liberalen Gamern und möchte dich bei uns herzlich willkommen heißen!<br />
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
Ist etwas falsch? Kein Problem! Deine Mitgliedsdaten kannst du selbst anpassen, in unserem Mitgliedersystem unter <a href="https://intern.liberale-gamer.gg">https://intern.liberale-gamer.gg</a>. Dein Passwort musst du über die „Passwort vergessen“-Funktion einmalig neu setzen.<br />
Im Mitgliedersystem hast du außerdem Zugriff auf vereinsinterne Dokumente und kannst den Status unserer Gameserver einsehen. Außerdem findest du dort Einladungslinks zu all unseren WhatsApp-Gruppen.<br />
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
Die Links zu unseren WhatsApp-Gruppen findest du wie erwähnt in unserem Mitgliedersystem.<br />
<br />
Falls du irgendwelche Fragen hast, kannst du dich jederzeit gerne an mich wenden.<br />
<br />
Liebe Grüße<br />
<br />
{current_user.vorname} {current_user.name}<br />
<br />
<br />
————————————————————————————————<br />
<br />
Liberale Gamer e.V.<br />
<br />
{current_user.vorname} {current_user.name}<br />
Mitgliederbetreuung<br />
<br />
Mobil:  {current_user.mobil}<br />
<br />
<a href="mailto:{current_user.email}">{current_user.email}</a><br />
<a href="https://www.liberale-gamer.gg">www.liberale-gamer.gg</a><br />"""

    if request.method == 'GET':
        return render_template('send_mail.html',user = user, geburtsdatum=geburtsdatum,\
        erstellungsdatum=erstellungsdatum, text=text, subject=subject)
    
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
            get_key.delete(user.schluessel)
            vorname = user.vorname
            db.session.delete(user)
            db.session.commit()
            flash('Mitglied gelöscht. <a onclick="copyText(\'' + vorname + '\')" class="linkinflash">Text für Mail kopieren</a>')
            return render_template('confirm_edit.html', confirm_delete=1, user=user)
        if "aktualisieren" in request.form:
            user_old = copy.copy(user)
            if current_user.id == user.id and str(current_user.rechte) != request.form['rechte']:
                current_user.rechte = request.form['rechte']
                db.session.commit()
                flash('Eigene Berechtigungen aktualisiert')
                return redirect(url_for('home'))
            for item in user.__dict__:      
                try:
                    if request.form[item] == "":
                        continue
                    if request.form[item] == "-":
                        vars(user)[item] = ""
                    elif str(vars(user)[item]) != request.form[item]:
                        vars(user)[item] = request.form[item]
                except:
                    pass        
            return render_template('confirm_edit.html', edit=1, user_old=user_old,user=user, geburtsdatum=geburtsdatum,\
            erstellungsdatum=erstellungsdatum)      
        if "payed" in request.form:
            user_old = copy.copy(user)
            user.payed_till += 1
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
            user.payed_till = request.form["payed_till"]
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
        payed_till = datetime.now().year - 1
        new = new_user(request.form["vorname"],request.form["name"], request.form["sex"],\
        request.form["strasse"], request.form["hausnummer"],request.form["plz"],\
        request.form["ort"], geburtsdatum,int(time.time()),\
        request.form["mobil"], request.form["email"], request.form["emailtext"],\
        geburtsdatum_string, erstellungsdatum_string, payed_till)
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
        user_add.payed_till = request.form["payed_till"]
        user_add.mobil = request.form["mobil"]
        user_add.email = request.form["email"]
        user_add.forum_id = 1
        user_add.forum_username = request.form["vorname"]
        user_add.sonstiges = request.form["emailtext"]
        user_add.schluessel = get_key.get()
        user_add.ukey = ""
        user_add.credential_id = ""
        user_add.pub_key = ""
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
