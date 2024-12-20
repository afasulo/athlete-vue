# app/models/hittrax_models.py

from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'  # Keep original table for now
    
    id = db.Column(db.BigInteger, primary_key=True)
    unitid = db.Column(db.BigInteger)
    firstname = db.Column(db.Text)
    lastname = db.Column(db.Text)
    username = db.Column(db.Text)
    password = db.Column(db.Text)
    created = db.Column(db.DateTime)
    email = db.Column(db.Text)
    stadium = db.Column(db.BigInteger)
    skilllevel = db.Column(db.BigInteger)
    gametype = db.Column(db.BigInteger)
    height = db.Column(db.Float)
    role = db.Column(db.BigInteger)
    active = db.Column(db.BigInteger)
    weight = db.Column(db.Float)
    position = db.Column(db.BigInteger)
    bats = db.Column(db.BigInteger)
    throws = db.Column(db.BigInteger)
    school = db.Column(db.Text)
    hometown = db.Column(db.Text)
    graduationyear = db.Column(db.BigInteger)
    gender = db.Column(db.BigInteger)
    birthdate = db.Column(db.DateTime)
    
    sessions = db.relationship('Session', backref='user', lazy='dynamic',
                             foreign_keys='Session.userid')

    @property
    def heightfeet(self):
        return self.height * 3.28084 if self.height else None

    @property
    def weightlbs(self):
        return self.weight * 2.20462 if self.weight else None

class Session(db.Model):
    __tablename__ = 'session'  # Keep original table for now
    
    id = db.Column(db.BigInteger, primary_key=True)
    unitid = db.Column(db.BigInteger)
    userid = db.Column(db.BigInteger, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime)
    stadium = db.Column(db.BigInteger)
    type = db.Column(db.BigInteger)
    skilllevel = db.Column(db.BigInteger)
    gametype = db.Column(db.BigInteger)
    maxpitchvel = db.Column(db.Float)
    maxexitvel = db.Column(db.Float)
    avgpitchvel = db.Column(db.Float)
    avgexitvel = db.Column(db.Float)
    avgelevation = db.Column(db.Float)
    avgdistance = db.Column(db.Float)
    maxdistance = db.Column(db.Float)
    pitchcount = db.Column(db.BigInteger)
    hitcount = db.Column(db.BigInteger)
    singles = db.Column(db.BigInteger)
    doubles = db.Column(db.BigInteger)
    triples = db.Column(db.BigInteger)
    homeruns = db.Column(db.BigInteger)
    foulballs = db.Column(db.BigInteger)
    strikes = db.Column(db.BigInteger)
    balls = db.Column(db.BigInteger)
    avg = db.Column(db.Float)
    slg = db.Column(db.Float)
    active = db.Column(db.BigInteger)
    strikezonewidth = db.Column(db.Float)
    
    plays = db.relationship('Play', backref='session', lazy='dynamic',
                          foreign_keys='Play.sessionid')

    # Add conversion properties
    @property
    def maxpitchvelmph(self):
        return self.maxpitchvel * 2.23694 if self.maxpitchvel else None

    @property
    def maxexitvelmph(self):
        return self.maxexitvel * 2.23694 if self.maxexitvel else None

    @property
    def avgpitchvelmph(self):
        return self.avgpitchvel * 2.23694 if self.avgpitchvel else None

    @property
    def avgexitvelmph(self):
        return self.avgexitvel * 2.23694 if self.avgexitvel else None

    @property
    def avgdistancefeet(self):
        return self.avgdistance * 3.28084 if self.avgdistance else None

    @property
    def maxdistancefeet(self):
        return self.maxdistance * 3.28084 if self.maxdistance else None

class Play(db.Model):
    __tablename__ = 'plays'  # Keep original table for now
    
    id = db.Column(db.BigInteger, primary_key=True)
    sessionid = db.Column(db.BigInteger, db.ForeignKey('session.id'))
    timestamp = db.Column(db.DateTime)
    exitballvel1 = db.Column(db.Float)
    exitballvel2 = db.Column(db.Float)
    exitballvel3 = db.Column(db.Float)
    distance = db.Column(db.Float)
    pitchvel = db.Column(db.Float)
    result = db.Column(db.BigInteger)
    type = db.Column(db.BigInteger)
    fielder = db.Column(db.BigInteger)
    quadrant = db.Column(db.BigInteger)
    pitchtype = db.Column(db.BigInteger)
    elevation = db.Column(db.Float)
    grounddist = db.Column(db.Float)
    active = db.Column(db.BigInteger)
    exitvelo = db.Column(db.Float)
    points = db.Column(db.BigInteger)

    # Add conversion properties
    @property
    def exitvelmph(self):
        return self.exitvelo * 2.23694 if self.exitvelo else None

    @property
    def distancefeet(self):
        return self.distance * 3.28084 if self.distance else None

    @property
    def pitchvelmph(self):
        return self.pitchvel * 2.23694 if self.pitchvel else None

    @property
    def grounddistfeet(self):
        return self.grounddist * 3.28084 if self.grounddist else None