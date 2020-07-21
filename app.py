from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager , UserMixin , login_required ,login_user, logout_user,current_user

from datetime import timedelta


app = Flask(__name__)
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(minutes=5)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    complete = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))
    tasks = db.relationship('Todo',backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password

db.create_all()

@login_manager.user_loader
def get(id):
    return User.query.get(id)

#home
@app.route('/',methods=['GET'])
def get_home():
    return render_template('home.html')

#register
@app.route('/register',methods=['GET'])
def get_signup():
    return render_template('register.html')

@app.route('/register',methods=['POST'])
def signup_post():
    username = request.form['username']
    password = request.form['password']
    confirm = request.form['confirm']
    user0 = User.query.filter_by(username=username).first()

    if password == confirm and not user0:
        user = User(username=username,password=password)
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(username=username).first()
        session['id'] = user.id
        login_user(user)
        flash("Successfully registred","success")
        return redirect('/login')
    else:
        flash("Passwords does not match or user already exists","danger")
        return render_template('register.html')
        
    
    #else:
     #   return render_template("register.html")

#login
@app.route('/login',methods=['GET'])
def get_login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    session.pop("user", None)
    session.permanent = True
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if 'id' in session:
        session['id']=user.id
    else:
        session['id'] = user.id

    login_user(user)
    return redirect(url_for('user'))

#user
@app.route('/user')
def user():
        return redirect(url_for('index'))


#logout
@app.route('/logout',methods=['GET'])
def logout():
    logout_user()
    return redirect('/login')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        todo = Todo(text=request.form['task'], complete=False, owner_id=session['id'])
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('index'))

    todos = Todo.query.filter_by(owner_id = session['id'])
    return render_template('index.html', todos=todos)

@app.route('/complete/<int:id>')
def complete(id):
    todo = Todo.query.get_or_404(id)
    todo.complete=True
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    todo = Todo.query.get_or_404(id) 
    db.session.delete(todo)
    db.session.commit()

    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
