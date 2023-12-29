from .extensions import db
from flask import render_template, redirect, url_for, flash, request,Blueprint,jsonify,make_response,session
from .models import User,Event,Session, summary_calculation
from flask_login import login_user, logout_user, current_user,login_required
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#routesa initten app geliyor 
main=Blueprint("main", __name__)

@main.route('/<int:user_id>')
@main.route('/home/<int:user_id>')
def home_page(user_id):
    render_template('home.html')

@main.route('/register', methods=['GET', 'POST'])
def register_page():

    data = request.get_json()
    unique_id=str(uuid.uuid4())
    if not data:
        return make_response("invalid content type",415)
    
    if User.query.filter_by(username=data["username"]).first():
        return jsonify(message="Bu kullanıcı adı zaten kullanılıyor."),409
    
    
    if User.query.filter_by(email_address=data["email"]).first():
        return jsonify(message="Bu email zaten kullanılıyor."),409
    
    hashed_password=generate_password_hash(data["password"])
    
    user_to_create = User(id=unique_id,
                        username=data['username'],
                          email_address=data['email'],
                          password_hash=hashed_password)  # Burada şifre hash'lenmelidir
     # Kullanıcıyı veritabanına ekle
    
    try:
        db.session.add(user_to_create)
        db.session.commit()
        return jsonify({"Message":"Success"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Kullanıcı kaydedilemedi.', 'error': str(e)}), 500
    # Başarılı kayıt için JSON cevabı döndür

@main.route('/login', methods=['GET', 'POST'])
def login_page():
    data=request.get_json()
    
    if not data:
        return make_response("invalid content type",415)
    
    user=User.query.filter_by(username=data["username"]).first()
    #kullanıcı adı bulunduysa
 
    if (user):    
        if check_password_hash(user.password_hash,data["password"]):
            session=create_session(user.id)
            return jsonify({"Message":"Success"})
        else:
            return jsonify(message="Şifreler uyuşmuyor"),406
    else:
        return jsonify(message="Başarısız"), 404
    
def create_session(user_id):
    new_session = Session(
        user_id=user_id,
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    db.session.add(new_session)
    db.session.commit()
    return new_session

def check_session_active(session_id):
    session = Session.query.get(session_id)
    if session and session.is_active:
        return True
    return False

#@login_required
@main.route('/api/events', methods=['POST'])
def create_event():
    data = request.get_json()
    #title date owner id
    unique_id=str(uuid.uuid4())
    data["category"]= str(data["category"]).lower()
    categories=["hobby", "study", "sports", "chores","miscellaneous"]
    
    if data["category"] not in categories:
        return jsonify("Category is not valid!"),201
    else:
        new_event = Event(id=unique_id,
                      title=data['title'], 
                      date=data['date'],
                      start_time=data["start_time"],
                      end_time=data["end_time"],
                      category=data["category"])
        new_event.duration_calculation()
        db.session.add(new_event)
        db.session.commit()
  

    return jsonify({'message': 'new event created'}), 201


@main.route('/api/events/summary', methods=['GET'])
def show_summary():
    data = request.get_json()
    year = data["year"]
    month = data["month"]
    day = data["day"]
    d = date(int(year),int(month), int(day))
    categories = {
        "hobby": 0, 
        "study" : 0, 
        "sports" : 0, 
        "chores" : 0,
        "miscellaneous" : 0
    }
    
    time_period = data["time_period"]
    if time_period == 1 :
        
        if not (Event.query.filter_by(date=d).all()):
            return jsonify({'message': 'no events available'})
        else:
            for event in Event.query.filter_by(date=d).all():
                duration = float(event.duration)
                categories[event.category] += duration
            plt.pie(values, labels=labels, autopct='%1.1f%%')
            plt.show() 
        
    elif time_period == 2 :
        week = d.strftime("%W")
        for event in Event.query.all():
            if event.date.strftime("%Y") == year and event.date.strftime("%W") == week:
                duration = float(event.duration)
                categories[event.category] += duration
        labels = list(categories.keys())
        values = list(categories.values())
        if values.count(0) == 5:
            return jsonify({'message': 'no events available'})
        else:
            plt.pie(values, labels=labels, autopct='%1.1f%%')
            plt.show()
                     
                   
    elif time_period == 3 :
        for event in Event.query.all():
            if event.date.strftime("%m") == month and event.date.strftime("%Y") == year:
                duration = float(event.duration)
                categories[event.category] += duration
        labels = list(categories.keys())
        values = list(categories.values())
        if values.count(0) == 5:
            return jsonify({'message': 'no events available'})
        else:
            plt.pie(values, labels=labels, autopct='%1.1f%%')
            plt.show()
            
    elif time_period == 4 :
        for event in Event.query.all():
            if event.date.strftime("%Y") == year:     
                duration = float(event.duration)
                categories[event.category] += duration
        labels = list(categories.keys())
        values = list(categories.values())
        if values.count(0) == 5:
            return jsonify({'message': 'no events available'})
        else:
            plt.pie(values, labels=labels, autopct='%1.1f%%')
            plt.show() 
    
    else:
        return jsonify({'message': 'invalid number of time period'})

    return jsonify({'message': 'summary has showed'})
    

@login_required
@main.route('/api/events/<date>', methods=['GET'])
def get_events(date):
    date = datetime.strptime(date, '%Y-%m-%d').date()
    events = Event.query.filter_by(date=date).all()
    return jsonify([{
        'id': event.id,
        'title': event.title,
        'date': event.date,
    } for event in events])
            
@login_required
@main.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))









