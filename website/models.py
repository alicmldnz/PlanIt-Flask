from flask_login import UserMixin
from .extensions import db,bcrypt
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import matplotlib.pyplot as plt

class User(db.Model, UserMixin):
    __tablename__="users"
    id=db.Column(db.String(),primary_key=True)
    username = db.Column(db.String(length=30),nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=256), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=1000)
    events = db.relationship('Event', backref='owned_user', lazy=True)

class Event(db.Model):
    __tablename__="events"
    id = db.Column(db.String(), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.String(), nullable=False)
    owner = db.Column(db.String(), db.ForeignKey('users.id'),nullable=True)
    category = db.Column(db.String(), nullable=False)


    def duration_calculation(self):
        sts=self.start_time
        ste=self.end_time
        t1=datetime.strptime(sts, "%H.%M.%S")
        t2=datetime.strptime(ste, "%H.%M.%S")
        delta= t2-t1
        self.duration=delta.total_seconds()


class Session(db.Model):
    __tablename__="sessions"
    user_id = db.Column(db.String(), db.ForeignKey('users.id'),primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

@property
def is_active(self):
    return datetime.utcnow() < self.expires_at
     

def summary_calculation(categories):
    labels = list(categories.keys())
    values = list(categories.values())
    if values.count(0) == 5:
        return jsonify({'message': 'no events available'})
    else:
        plt.pie(values, labels=labels, autopct='%1.1f%%')
        plt.show()
    
    
    
