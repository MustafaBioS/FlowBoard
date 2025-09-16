from flask import Flask, render_template, url_for, request, flash, redirect
from flask_login import login_required, login_user, current_user, UserMixin, LoginManager, logout_user
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from flask_migrate import Migrate
from datetime import datetime, timezone

# APP

app = Flask(__name__)
app.secret_key = 'FlowBoardAdminKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(uid):
    return Users.query.get(int(uid))

# MODELS

class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128), nullable=False)

    def get_id(self):
        return str(self.uid)

class Tasks(db.Model):
    tid = db.Column(db.Integer, primary_key = True, autoincrement=True)
    tcontent = db.Column(db.String(64), nullable=False)
    tdate_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey('Users.uid'), nullable=False)

class Notes(db.Model):
    nid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ntitle = db.Column(db.String(64), nullable=False)
    ncontent = db.Column(db.Text, nullable=False)
    ndate_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey('Users.uid'), nullable=False)

class Bookmarks(db.Model):
    bid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    btitle = db.Column(db.String(64), nullable=False)
    blink = db.Column(db.Text, nullable=False)
    bdate_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey('Users.uid'), nullable=False)



# Routes

@app.route('/')
def main():
    all_notes = Notes.query.all()
    return render_template('index.html', newnote=all_notes)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login/login.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter(Users.username == username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login Successful', 'homeflash')
            return redirect(url_for('main'))
        else:
            flash("Incorrect Username or Password", 'failed')
            return redirect(url_for('login'))



@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('login/signup.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            user = Users(username=username, password=hashed_password)

            db.session.add(user)
            db.session.commit()
            flash("Account Created Successfully", "success")
            return redirect(url_for('login'))

        except sqlalchemy.exc.IntegrityError: 
            db.session.rollback()
            flash("Username Already Taken", 'failed')
            return redirect(url_for('signup'))
    
    else:
        flash('Signup Failed', 'failed')
        return redirect(url_for('signup'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out", 'homeflash')
    return redirect(url_for('main'))

@app.route('/tasks', methods=['POST', 'GET'])
@login_required
def tasks():
    tasks = Tasks.query.filter_by(user_id=current_user.uid).all()
    return render_template('tasks/tasks.html', tasks=tasks)
    


    
@app.route('/tasks/add', methods=['POST', 'GET'])
@login_required
def addtask():
    if request.method == 'GET':
        return render_template('tasks/addtask.html')
    
    if request.method == 'POST':

        task = request.form.get('task')

        newtask = Tasks(tcontent=task, user_id=current_user.uid)

        db.session.add(newtask)
        db.session.commit()

        flash('Task Added Successfully', 'success')
        return redirect(url_for("tasks"))
    
@app.route('/tasks/delete/<int:task_id>', methods=['POST'])
def deletetask(task_id):
    
    task = Tasks.query.get_or_404(task_id)

    db.session.delete(task)
    db.session.commit()
    flash("Task Deleted Successfully", 'success')
    return redirect(url_for('tasks'))

@app.route('/notes')
@login_required
def notes():
    all_notes = Notes.query.filter_by(user_id=current_user.uid).all()

    return render_template('notes/notes.html', newnote=all_notes)

@app.route('/notes/add', methods=['POST', 'GET'])
@login_required
def addnotes():
    if request.method == 'GET':
        return render_template('notes/addnotes.html')
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        newnote = Notes(ntitle=title, ncontent=content, user_id=current_user.uid)
        
        db.session.add(newnote)
        db.session.commit()
        flash('Note Created Successfully', 'success')
        return redirect(url_for('notes'))

@app.route('/notes/delete/<int:note_id>', methods=['POST'])
@login_required
def deletenotes(note_id):
    if request.method == 'POST':
        note = Notes.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        flash('Note Deleted Successfully', 'success')
        return redirect(url_for('notes'))

@app.route('/notes/edit/<int:note_id>', methods=['GET', 'POST'])
def editnotes(note_id):
    note = Notes.query.get_or_404(note_id)
    if request.method == 'GET':
        return render_template('notes/edit.html', note=note)
    if request.method == 'POST':
        note.ntitle = request.form.get('newtitle')
        note.ncontent = request.form.get('newcontent')
        db.session.commit()
        flash('Note Edited Successfully', 'success')
        return redirect(url_for('notes'))

@app.route('/bookmarks')
@login_required
def bookmarks():
    bookmark = Bookmarks.query.filter_by(user_id = current_user.uid).all()
    return render_template('bookmarks/bookmarks.html', newbm=bookmark)

@app.route('/newbookmark', methods = ['GET', 'POST'])
@login_required
def addbm():
    if request.method == 'GET':
        return render_template('bookmarks/addbm.html')
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('URL')

        newbm = Bookmarks(btitle=name, blink=url, user_id = current_user.uid)
        db.session.add(newbm)
        db.session.commit()
        flash('Bookmark Created Successfully', 'bookmark')
        return redirect(url_for('bookmarks'))
    
@app.route('/bookmark/edit/<int:bm_id>', methods=['GET', 'POST'])
@login_required
def editbm(bm_id):
    bm = Bookmarks.query.get_or_404(bm_id)
    if request.method == 'GET':
        return render_template('bookmarks/editbm.html', bm=bm, bm_id =bm.bid)
    if request.method == 'POST':
        bm.btitle = request.form.get('name')
        bm.blink = request.form.get('URL')
        db.session.commit()
        flash('Bookmark Edited Successfully', 'bookmark')
        return redirect(url_for('bookmarks'))

@app.route('/bookmark/delete/<int:bm_id>', methods=['POST'])
@login_required
def deletebm(bm_id):
    if request.method == 'POST':
        bm = Bookmarks.query.get_or_404(bm_id)
        db.session.delete(bm)
        db.session.commit()
        flash('Bookmark Deleted Successfully', 'bookmark')
        return redirect(url_for('bookmarks'))

@app.errorhandler(404)
def invalid(e):
    flash('The URL Entered Is Invalid', 'failed')
    return redirect(url_for('bookmarks'))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

# Run

if __name__ == '__main__':
    app.run(debug=True)