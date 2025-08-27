from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timezone

# APP

app = Flask(__name__)
app.secret_key = 'FlowBoardAdminKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

# MODELS

class Users(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(64), nullable=False)

class Tasks(db.Model):
    tid = db.Column(db.Integer, primary_key = True)
    tcontent = db.Column(db.String(64), nullable=False)
    tdate_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
class Notes(db.Model):
    nid = db.Column(db.Integer, primary_key=True)
    ntitle = db.Column(db.String(64), nullable=False)
    ncontent = db.Column(db.Text, nullable=False)
    ndate_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Bookmarks(db.Model):
    bid = db.Column(db.Integer, primary_key=True)
    btitle = db.Column(db.String(64), nullable=False)
    blink = db.Column(db.Text, nullable=False)
    bdate_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# Routes

@app.route('/')
def main():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        pass


@app.route('/signup')
def signup():
    pass


@app.route('/tasks')
def tasks():
    pass


@app.route('/notes')
def notes():
    pass


@app.route('/bookmarks')
def bookmarks():
    pass

# Run

if __name__ == '__main__':
    app.run(debug=True)