from main import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    todo_items = relationship('ToDo', back_populates='person')

    result_all = db.Column(JSON)
    result_no_stop_words = db.Column(JSON)

    def __init__(self, username, password, todo_items, result_all, result_no_stop_words):
        self.username = username
        self.password = password
        self.todo_items = todo_items
        self.result_all = result_all
        self.result_no_stop_words = result_no_stop_words

    def __repr__(self):
        return '<id {}>'.format(self.id)

class ToDo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False)
    deadline = db.Column(db.String, nullable=False)
    details = db.Column(db.String(200), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    person = relationship('User', back_populates='todo_items')

    result_all = db.Column(JSON)
    result_no_stop_words = db.Column(JSON)

    def __init__(self, title, deadline, details, person_id, result_all, result_no_stop_words):
        self.title = title
        self.deadline = deadline
        self.details = details
        self.person_id = person_id
        self.result_all = result_all
        self.result_no_stop_words = result_no_stop_words

    def __repr__(self):
        return '<id {}>'.format(self.id)

db.create_all()