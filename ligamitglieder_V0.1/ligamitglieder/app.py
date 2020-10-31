from flask import Flask , request, render_template, session, flash, redirect, url_for, g, jsonify
from flask_sqlalchemy import SQLAlchemy
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



app = Flask(__name__)

#MySQL Verbindung
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://liga_mitglieder:13fh89Fls2Zj@localhost/liga_intern_de'
'''
app.config['MYSQL_USER'] = 'liga_mitglieder'
app.config['MYSQL_PASSWORD'] = '13fh89Fls2Zj'
app.config['MYSQL_DB'] = 'liga_intern_de'
'''


db = SQLAlchemy(app)

ma = Marshmallow(app)

login_manager = LoginManager()
login_manager.init_app(app)

class new_user():
  def __init__(self, vorname, name, sex, strasse, hausnummer,\
  plz, ort, geburtsdatum, erstellungsdatum, mobil, email):
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

class kunden(UserMixin, db.Model):
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
    telefon = db.Column(db.String(30), default="NULL")
    fax = db.Column(db.String(30), default="NULL")
    #sonstiges = db.Column(db.String(30), default="NULL")
    passwort = db.Column(db.String(30), default="12345")
    forum_id = db.Column(db.String(30))
    forum_username = db.Column(db.String(30))
    forum_passwort = db.Column(db.String(30), default="12345")
    #stichworte = db.Column(db.String(30), default="NULL")
    latitude = db.Column(db.String(30), default="NULL")
    longitude = db.Column(db.String(30), default="NULL")
    last_aktivity = db.Column(db.String(30), default=0)
    
class kundenSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = kunden
        load_instance = True  


class verkaeufer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), unique = True)
    kuerzel = db.Column(db.String(2))
    passwort = db.Column(db.String(50))
    email = db.Column(db.String(50))
    token = db.Column(db.String(50))
    tokenttl = db.Column(db.Integer)
    
#Redirect if trying to access protected page
login_manager.login_view = "login" 
#Secret session key (TODO: RANDOMIZE)
ran = np.random.randint(9999999999) * np.random.randint(9999999999)
app.secret_key = hashlib.sha3_256(str(ran).encode('utf-8')).hexdigest()


@login_manager.user_loader
def load_user(user_id):
    return verkaeufer.query.get(int(user_id))  
    
@app.route('/')
def show_entries():
    return redirect(url_for('login'))
    
@app.route('/index.html')
def index():
    return redirect(url_for('login'))   
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if current_user.is_authenticated == True:
        return redirect('/home')
    else:
        pass    
    if request.method == 'POST':
        user = verkaeufer.query.filter_by(kuerzel=request.form['username']).first()
        if user == None:
            error = 'username does not exist'
            return render_template('login.html',error=error)
        password = hashlib.sha3_256(str(request.form['password']).encode('utf-8')).hexdigest()
        if password == user.passwort:
            login_user(user,remember=True,duration=timedelta(300))
            return render_template('home.html',error=error)
        else:
            error = 'wrong password'
    else:
        password = None
        pass
    return render_template('login.html',error=error)

    
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        if "old_password" in request.form:
            password = hashlib.sha3_256(str(request.form['old_password']).encode('utf-8')).hexdigest()
            if password == current_user.passwort and request.form['new_password'] == request.form['confirm_password'] and request.form['new_password'] != '':
                flash('Password updated successfully')
                new_pw = hashlib.sha3_256(str(request.form['new_password']).encode('utf-8')).hexdigest()
                current_user.passwort = new_pw
                db.session.commit()
                return render_template('home.html') 
            else:
                if password != current_user.passwort:
                    flash('wrong old password')
                if request.form['new_password'] != request.form['confirm_password']:
                    flash('entered two different passwords')
                if request.form['new_password'] == '':
                    flash('Please enter a new password')
        if "email" in request.form:
            current_user.email = request.form['email']
            db.session.commit()
            flash('new email set')
            return render_template('home.html')
    else:
        pass
    return render_template('home.html')

#Routine for forgotten password
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        email = request.form['email']
        token = hashlib.sha3_256(str(np.random.randint(999999999999999)).encode('utf-8')).hexdigest()
        token2 = hashlib.sha3_256(str(np.random.randint(999999999999999)).encode('utf-8')).hexdigest()
        if email != "":
            user = verkaeufer.query.filter_by(email=request.form['email']).first()
        try:
            if user.email == email:
                user.token = token + token2
                user.tokenttl = int(time.time()) + 300
                db.session.commit()
        except:
            flash('Email is not in database')
            return render_template('reset.html')
        
        sender = "LiGa Mitgliederdatenbank <reset@liberale-gamer.gg>"

       

        text = """\
Hallo {},

Der Link zum zurücksetzen deines Passworts lautet: {}""".format(user.name,"https://mitgliederverwaltung.liberale-gamer.gg/"+"reset/"+user.token) 

        mailer.send_email(sender, email, "Password reset", text)
        flash('Reset Email sent to {}'.format(email))
    return render_template('reset.html')
    
#Actually reset the password
@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_pw(token):
    user = verkaeufer.query.filter_by(token=token).first()
    if user.tokenttl < int(time.time()):
        flash('This token has expired')
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
                    flash('entered two different passwords')
                if request.form['new_password'] == '':
                    flash('Please enter a new password')            
    return render_template('reset_pw.html',token=token)


   
@app.route('/new')
@login_required
def new():
    
    return render_template('new.html')

    
@app.route('/database')
@login_required
def database():
    
    all_users = kunden.query.all()
    kundenschema = kundenSchema(many=True)
    output = kundenschema.dumps(all_users)
    data_json = jsonify({'name' : output})
    return render_template('database.html',output = output)
    #return output
    
@app.route('/edit/<user_id>')
@login_required
def edit(user_id):
    user = kunden.query.filter_by(id=user_id).first()
    

    geburtsdatum = format(datetime.fromtimestamp(user.geburtsdatum+7200), '%d.%m.%Y')
    erstellungsdatum = format(datetime.fromtimestamp(user.erstellungsdatum), '%d.%m.%Y')
    

    session['user_id'] = user_id
        
    return render_template('edit.html',user = user, geburtsdatum=geburtsdatum,\
    erstellungsdatum=erstellungsdatum)
    
    
@app.route('/confirm_edit',methods=['GET','POST'])
@login_required
def confirm_edit():
    if request.method == 'POST':
        user = kunden.query.filter_by(id=session["user_id"]).first()
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
                    if vars(user)[item] != request.form[item] and request.form[item] != "":
                        vars(user)[item] = request.form[item]
                except:
                    pass        
            return render_template('confirm_edit.html', edit=1, user_old=user_old,user=user, geburtsdatum=geburtsdatum,\
    erstellungsdatum=erstellungsdatum)            
            flash('Prompted change')
        if "confirm_edit" in request.form:
            user.name = request.form["name"]
            user.vorname = request.form["vorname"]
            user.strasse = request.form["strasse"]
            user.hausnummer = request.form["hausnummer"]
            user.plz = request.form["plz"]
            user.ort = request.form["ort"]
            user.email = request.form["email"]
            user.mobil = request.form["mobil"]
        
            db.session.commit()
        
            flash('Änderungen übernommen')
            return redirect(url_for('edit',user_id=str(user.id)))
        flash(request.form)
    return render_template('confirm_edit.html')
    
@app.route('/confirm_new',methods=['GET','POST'])
@login_required
def confirm_new():
    if "new" in request.form and request.method == 'POST':
        flash('Standard new prompted')
        flash(request.form["vorname"])
        geburtsdatum = int(time.mktime(datetime.strptime(request.form["geburtsdatum"], "%Y-%m-%d").timetuple()))+7200
        new = new_user(request.form["vorname"],request.form["name"], request.form["sex"],\
        request.form["strasse"], request.form["hausnummer"],request.form["plz"],\
        request.form["ort"], geburtsdatum,int(time.time()),\
        request.form["mobil"], request.form["email"])
        return render_template('confirm_new.html', confirm=1, new=new)
    if "smart" in request.form and request.method == 'POST':
        flash('Smart new prompted')
        return render_template('confirm_new.html', confirm=1, new=new)
        #TODO: Build a regex transcriber for the email
    if "confirm_new" in request.form and request.method == 'POST':
        
        user_add = kunden()
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
        
        return render_template('confirm_new.html', created=1)
    
    return render_template('confirm_new.html')
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Du wurdest ausgeloggt')
    return redirect(url_for('login'))
