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

class Bookmarks(db.Model):
    bid = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
        return render_template('login/login.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter(Users.username == username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main'))
        else:
            flash("Incorrect Username or Password", 'flash')
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
            flash("Account Created Successfully", "flash")
            return redirect(url_for('login'))

        except sqlalchemy.exc.IntegrityError: 
            db.session.rollback()
            flash("Username Already Taken", 'flash')
            return redirect(url_for('signup'))
    
    else:
        flash('Signup Failed', 'flash')
        return redirect(url_for('signup'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out", 'flash')
    print('working')
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

        flash('Task Added Successfully', 'flash')
        return redirect(url_for("tasks"))
    
@app.route('/tasks/delete/<int:task_id>', methods=['POST'])
def deletetask(task_id):
    
    task = Tasks.query.get_or_404(task_id)

    db.session.delete(task)
    db.session.commit()
    flash("Task Deleted Successfully", 'flash')
    return redirect(url_for('tasks'))

@app.route('/notes')
@login_required
def notes():
    return render_template('notes/notes.html')


@app.route('/bookmarks')
@login_required
def bookmarks():
    pass

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

# Run

if __name__ == '__main__':
    app.run(debug=True)