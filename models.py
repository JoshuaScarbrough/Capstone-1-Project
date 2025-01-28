from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

""" Begins to create the classes that build up the website. Part of the capstone1 database """

class User(db.Model):
    """ A user account for the accountabilit-e website """

    __tablename__ = 'users'

    id = db.Column( db.Integer, primary_key=True)

    first_name = db.Column( db.Text, nullable = False)

    last_name = db.Column( db.Text, nullable = False)

    username = db.Column( db.Text, nullable=False, unique=True)

    password = db.Column( db.Text, nullable=False)

    email = db.Column( db.Text, nullable=False, unique=True)

    profile_picture = db.Column( db.Text, default="https://www.shutterstock.com/image-vector/user-profile-icon-vector-avatar-600nw-2220431045.jpg", nullable=True)

    user_mood = db.Column( db.Text, nullable=True)

    goal = db.relationship('Goal')

    schedule = db.relationship('Schedule')

    toDoTask = db.relationship('TodoTask') 

    @classmethod
    def register(cls, username, password, first_name, last_name, email):

        hashed = bcrypt.generate_password_hash(password)

        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8, first_name=first_name, last_name=last_name, email=email)
    
    @classmethod
    def authenticate(cls, username, password):

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False



class Verse(db.Model):
    """ Verses that are going to be used in part of the application to uplift the users. Gonna be used as an internal RESTFUL API """

    __tablename__ = 'verses'

    id = db.Column( db.Integer, primary_key=True)

    mood_code = db.Column( db.Text, nullable=False)

    verse = db.Column(db.Text, nullable=False)


""" 
Users are going to have goals and plans to achieve those goals
"""
class Goal(db.Model):
    """ Every user is gonna have the ability to have short term or long term goals """

    __tablename__ = 'goals'

    id = db.Column( db.Integer, primary_key=True)

    user_id = db.Column( db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)

    goal_code = db.Column( db.Text, nullable=False)

    goal = db.Column( db.Text, nullable=False)


class Step(db.Model):
    """ Steps are going to be used to accomplish the goal """

    __tablename__ = 'steps'

    id = db.Column( db.Integer, primary_key=True)

    goal_id = db.Column( db.Integer, db.ForeignKey('goals.id'), nullable=False)

    step = db.Column( db.Text, nullable=False)

    end_date = db.Column(db.Date, nullable=False)


"""
Users are going to have schedules, that can have multiple schedule groups
these schedule groups are going to consist of the days of the week
each day of the week is / can have a different task group
each task group is going to have different tasks
"""
class Schedule(db.Model):
    """ Every user is going to be able to input their schedule """

    __tablename__ = 'schedules'

    id = db.Column( db.Integer, primary_key=True)
    
    user_id = db.Column( db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)


class Task(db.Model):
    """ These are the tasks that are going to be set by the user on their specific days of the week"""

    __tablename__ = 'tasks'

    id = db.Column( db.Integer, primary_key=True)

    timestamp = db.Column( db.Integer, nullable=False)

    day = db.Column(db.Text, nullable=False)

    entry = db.Column( db.Text, nullable=False)

    user_id = db.Column( db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)



class TodoTask(db.Model):
    """ These are the tasks that are going to be set by the user on their specific days of the week"""

    __tablename__ = 'todotasks'

    id = db.Column( db.Integer, primary_key=True)

    user_id = db.Column( db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)

    date_due = db.Column(db.Date, nullable=False)

    time = db.Column( db.Time)

    entry = db.Column( db.Text, nullable=False)



def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)