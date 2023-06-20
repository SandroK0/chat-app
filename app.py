from flask import Flask, redirect, request, render_template, session
from flask_socketio import SocketIO, send
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret!123'
socketio = SocketIO(app)


class Database():

    def __init__(self, db):
        self.db = db

    def add_user(self, user):

        conn = sqlite3.connect(self.db)
        c = conn.cursor()

        c.execute("INSERT INTO Users (nickname, password) VALUES (?, ?)",
                  (user.nickname, user.password))
        conn.commit()
        conn.close()

    def get_messages(self):

        conn = sqlite3.connect(self.db)
        c = conn.cursor()

        messages = c.execute("SELECT * FROM Messages").fetchall()

        conn.close()
        return messages

    def new_message(self, author, message):

        conn = sqlite3.connect(self.db)
        c = conn.cursor()

        c.execute("INSERT INTO Messages (author, message) VALUES (?, ?)",
                  (author, message))

        conn.commit()
        conn.close()

    def check_user(self, user):

        conn = sqlite3.connect(self.db)
        c = conn.cursor()

        search = c.execute(
            "SELECT * FROM Users WHERE nickname = ?", (user.nickname,)).fetchall()

        if search:
            if user.password == search[0][1]:
                return True
        else:
            return False


db = Database('Database.sqlite')


class User():

    def __init__(self, nickname, password):

        self.nickname = nickname
        self.password = password


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        nickname = request.form.get('nickname_input')
        password = request.form.get('password_input')

        if 'register' in request.form:
            return redirect('/register')

        if nickname and password:
            user = User(nickname, password)

        if (db.check_user(user)):
            session['user'] = user.nickname
            return redirect('/ChatRoom')

    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        nickname = request.form.get('nickname-input')
        password = request.form.get('password-input')
        repeatPassword = request.form.get('repeatpassword-input')

        if password != repeatPassword:
            return redirect('/register')

        user = User(nickname, password)
        db.add_user(user)
        return redirect('/')

    return render_template('register.html')


@app.route('/ChatRoom', methods=['GET', 'POST'])
def ChatRoom():    
    if 'user' in session:
        user = session['user']
        MESSAGES = db.get_messages()
        
        if request.method == 'POST':
            session.pop('user')
            return redirect('/')
        
    else:
        return redirect('/')
    return render_template('ChatRoom.html', messages=MESSAGES, session=session)


@socketio.on('new_message')
def handle_new_message(data):

    author = session['user']
    message = data['message']
    db.new_message(author, message)
    send({'author': author, 'message': message}, broadcast=True)


if __name__ == "__main__":

    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
