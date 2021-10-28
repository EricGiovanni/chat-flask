from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    username = db.Column(db.String(200), primary_key=True)
    password = db.Column(db.String(200))

#socketio = SocketIO(app)


@login_manager.user_loader
def get(id):
    return User.query.get(id)


@app.route('/chat', methods=['GET'])
@login_required
def get_home():
    return render_template('chat.html')


@app.route('/', methods=['GET'])
def get_login():
    return render_template('login.html')


@app.route('/register', methods=['GET'])
def get_register():
    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login_post():
    user = request.form['user']
    password = request.form['password']
    user = User.query.filter_by(user=user).first()
    login_user(user)
    return redirect('/')


@app.route('/register', methods=['POST'])
def signup_post():
    username = request.form['username']
    password = request.form['password']
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    user = User.query.filter_by(username=username).first()
    login_user(user)
    return redirect('/')


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/register')
# def register():
#     pass


# @app.route('/login')
# def login():
#     pass


# @socketio.on('message')
# def handleMessage(msg):
#     print('Message: ' + msg)
#     send(msg, broadcast=True)


# if __name__ == '__main__':
#     con = sqlite3.connect('users.db')
#     cur = con.cursor()
#     cur.execute(
#         "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, password TEXT)")
#     con.commit()
#     socketio.run(app)
