import passwords

class sql_config:
    def __init__(self, user, pw, db):
        self.user = user 
        self.pw = pw 
        self.db = db 
        
sql_config.user = 'liga_mitglieder'
sql_config.pw = passwords.sql
sql_config.db = 'liga_intern_de'
