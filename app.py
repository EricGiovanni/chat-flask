from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_socketio import SocketIO, emit
from decouple import config


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config("SQLITE", cast=str)
app.config['SECRET_KEY'] = config("SECRET_KEY", cast=str)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    def get_id(self):
        return self.username
    username = db.Column(db.String(200), primary_key=True)
    password = db.Column(db.String(200))


@login_manager.user_loader
def get(id):
    return User.query.get(id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/')


@app.route('/chat', methods=['GET'])
@login_required
def get_home():
    return render_template('chat.html')


@app.route('/', methods=['GET'])
def get_login():
    if current_user.is_authenticated:
        return redirect('/chat')
    return render_template('login.html')


@app.route('/register', methods=['GET'])
def get_register():
    if current_user.is_authenticated:
        return redirect('/chat')
    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username, password=password).first()
    if user is None:
        return redirect('/')
    login_user(user)
    return redirect('/chat')


@app.route('/register', methods=['POST'])
def register_post():
    if User.query.filter_by(username=request.form['username']).count() < 1:
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(username=username).first()
        login_user(user)
        return redirect('/chat')
    return redirect('/')


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect('/')


@socketio.on('message')
def handleMessage(msg):
    emit('message', current_user.username + " - " + msg, broadcast=True)


@socketio.on('image')
def handleImage(msg):
    print(msg)
    emit('image', msg, broadcast=True)


@socketio.on('join')
def join(username):
    emit('join', username, broadcast=True)


@socketio.on('leave')
def leave(username):
    emit('leave', current_user.username, broadcast=True)
    emit('message', current_user.username + " salió del chat", broadcast=True)


if __name__ == '__main__':
    db.create_all()
    socketio.run(app, debug=True)
